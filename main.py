import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import argparse, os, json, re, warnings
warnings.filterwarnings("ignore")
import pandas as pd
from dotenv import load_dotenv
import anthropic

load_dotenv()
os.environ.setdefault("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))


def pic50_to_class(pic50: float) -> str:
    if pic50 < 5.0:   return "inactive"
    elif pic50 < 6.0: return "weak"
    elif pic50 < 7.0: return "moderate"
    elif pic50 < 8.0: return "potent"
    else:             return "highly_potent"


def build_sar_summary(df: pd.DataFrame) -> str:
    """Build a concise SAR summary for Claude."""
    lines = ["Existing SAR data (45 CETP inhibitor compounds):\n"]

    # Per-scaffold stats
    for fam in sorted(df["compound_name"].str.split("_").str[0].unique()):
        fam_df = df[df["compound_name"].str.startswith(fam + "_")]
        lines.append(f"  {fam}: n={len(fam_df)}, mean_pIC50={fam_df['pic50'].mean():.2f}, "
                     f"range=[{fam_df['pic50'].min():.2f}, {fam_df['pic50'].max():.2f}]")

    # Top 3 compounds
    top3 = df.nlargest(3, "pic50")
    lines.append("\nTop 3 most potent:")
    for _, r in top3.iterrows():
        lines.append(f"  {r['compound_name']}: pIC50={r['pic50']:.2f}, SMILES={r['smiles']}")

    # Bottom 3
    bot3 = df.nsmallest(3, "pic50")
    lines.append("\nBottom 3 least potent:")
    for _, r in bot3.iterrows():
        lines.append(f"  {r['compound_name']}: pIC50={r['pic50']:.2f}, SMILES={r['smiles']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--input", required=True)
    parser.add_argument("--budget", type=int, default=3, help="Number of new compounds to propose")
    parser.add_argument("--model", default="claude-haiku-4-5-20251001")
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    df = pd.read_csv(args.input)
    client = anthropic.Anthropic()
    sar_summary = build_sar_summary(df)

    prompt = (
        f"You are a medicinal chemist designing the next round of CETP inhibitor experiments.\n\n"
        f"{sar_summary}\n\n"
        f"You have a budget to synthesize exactly {args.budget} new compounds.\n"
        f"Design {args.budget} compounds that would most effectively explore SAR gaps or improve potency.\n\n"
        f"For each proposed compound, respond as JSON array:\n"
        f'[{{"compound_name": "proposed_001", "smiles": "...", "predicted_pic50": <float>, '
        f'"scaffold_family": "...", "rationale": "one sentence explaining the design logic"}}, ...]'
    )

    print(f"\nPhase 67 — Experiment Designer")
    print(f"Model: {args.model} | Budget: {args.budget} compounds\n")

    response = client.messages.create(model=args.model, max_tokens=1024, messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in response.content if hasattr(b, "text"))

    json_match = re.search(r'\[.*\]', text, re.DOTALL)
    proposals = json.loads(json_match.group()) if json_match else []

    print(f"Proposals ({len(proposals)}):")
    for p in proposals:
        print(f"  {p.get('compound_name','?'):20s} | pred_pIC50={p.get('predicted_pic50','?'):>5} | "
              f"fam={p.get('scaffold_family','?'):5s} | {p.get('rationale','')[:70]}")

    usage = response.usage
    cost = (usage.input_tokens / 1e6 * 0.80) + (usage.output_tokens / 1e6 * 4.0)
    print(f"\nTokens: in={usage.input_tokens} out={usage.output_tokens} | Cost: ${cost:.4f}")

    with open(os.path.join(args.output_dir, "proposed_compounds.json"), "w", encoding="utf-8") as f:
        json.dump(proposals, f, indent=2, ensure_ascii=False)
    with open(os.path.join(args.output_dir, "experiment_report.txt"), "w", encoding="utf-8") as f:
        f.write(f"Phase 67 — Experiment Designer\n{'='*40}\n"
                f"Model: {args.model}\nBudget: {args.budget}\nProposals: {len(proposals)}\n"
                f"Tokens: in={usage.input_tokens} out={usage.output_tokens}\nCost: ${cost:.4f}\n")
    print("Done.")


if __name__ == "__main__":
    main()
