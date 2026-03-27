# Phase 67 — Claude as Experiment Designer (Suggest Next Compound)

**Version:** 1.0 | **Tier:** Standard | **Date:** 2026-03-27

## Goal
Given existing SAR data and a budget of 3 new compounds, ask Claude to design the next experiments.
Tests Claude's ability to reason about SAR gaps, propose novel modifications, and predict activity.

CLI: `python main.py --input data/compounds.csv --budget 3`

Outputs: proposed_compounds.json, experiment_report.txt

## Logic
- Load full compound library (45 compounds with SMILES, pIC50, scaffold family)
- Build an SAR summary: mean pIC50 per scaffold, best/worst compounds, activity cliffs
- Ask Claude: "Given this SAR data and a budget of 3 compounds, which should we synthesize next?"
- Require structured output: proposed SMILES, rationale, predicted pIC50, scaffold family
- Evaluate: are proposals structurally valid? Do predicted pIC50 values fall in reasonable range?
- Report: proposals with rationale, predicted potency, cost

## Key Concepts
- Claude as agentic experiment designer (not just classifier/reviewer)
- Input: full SAR context + explicit budget constraint
- Output: novel compound proposals with chemical reasoning
- Tests generative capability: Claude must invent SMILES, not just classify existing ones
- Structured JSON: `[{compound_name, smiles, predicted_pic50, rationale, scaffold_family}]`

## Verification Checklist
- [ ] Claude generates exactly 3 proposals matching the budget
- [ ] Each proposal includes SMILES, predicted pIC50, rationale
- [ ] Proposals reference existing SAR data (specific compounds or trends)
- [ ] One clean API call

## Risks
- Generated SMILES may be invalid (can validate with RDKit if rdkit available)
- Predicted pIC50 may be unrealistically high
- Claude may recycle existing compounds instead of proposing new ones
