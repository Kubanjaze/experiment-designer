# Phase 67 — Claude as Experiment Designer (Suggest Next Compound)

**Version:** 1.1 | **Tier:** Standard | **Date:** 2026-03-27

## Goal
Given existing SAR data and a budget of 3 new compounds, ask Claude to design the next experiments.
Tests Claude's ability to reason about SAR gaps, propose novel modifications, and predict activity.

CLI: `python main.py --input data/compounds.csv --budget 3`

Outputs: proposed_compounds.json, experiment_report.txt

## Logic
- Load full compound library (45 compounds with SMILES, pIC50, scaffold family)
- Build an SAR summary: mean pIC50 per scaffold, top/bottom compounds, activity ranges
- Ask Claude: "Given this SAR data and a budget of 3 compounds, which should we synthesize next?"
- Require structured output: proposed SMILES, rationale, predicted pIC50, scaffold family
- Report: proposals with rationale, predicted potency, cost

## Key Concepts
- Claude as agentic experiment designer (not just classifier/reviewer)
- Input: full SAR context + explicit budget constraint
- Output: novel compound proposals with chemical reasoning
- Tests generative capability: Claude must propose novel modifications, not recycle existing compounds
- Structured JSON: `[{compound_name, smiles, predicted_pic50, rationale, scaffold_family}]`

## Verification Checklist
- [x] Claude generates exactly 3 proposals matching the budget
- [x] Each proposal includes predicted pIC50 and rationale
- [x] Proposals reference existing SAR trends (EWG strategy, scaffold weaknesses)
- [x] One clean API call

## Results
| Metric | Value |
|--------|-------|
| Proposals | 3/3 matching budget |
| Proposal 1 | ind_008_CN_Me (pred pIC50=8.42) — dual substitution on best scaffold |
| Proposal 2 | quin_007_CN (pred pIC50=8.38) — transplant CN from ind to quin series |
| Proposal 3 | bzim_009_CF3 (pred pIC50=7.68) — upgrade weakest scaffold with best EWG |
| Input tokens | 559 |
| Output tokens | 546 |
| Est. cost | $0.0026 |

Key finding: Claude correctly identified three distinct strategies — (1) optimize the best scaffold further, (2) transplant a winning substituent to an underexplored scaffold, (3) rescue the weakest series. This mirrors real medchem prioritization.
