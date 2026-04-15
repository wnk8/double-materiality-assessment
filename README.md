# Double Materiality Assessment Tool

A Python-based, CSRD/ESRS-compliant **Double Materiality Assessment (DMA) Tool** for companies conducting materiality analyses under the Corporate Sustainability Reporting Directive (CSRD). Operationalizes the EFRAG methodology for assessing Impact Materiality (inside-out) and Financial Materiality (outside-in) across ESRS topics.

## Features

- Generates a pre-filled Excel IRO input template (20 IROs across 7 ESRS topics)
- Scores Impact and Financial Materiality using EFRAG methodology
- Produces a materiality matrix (matplotlib)
- Produces an ESRS heatmap (seaborn)
- Generates a full PDF report (ReportLab)
- Fully offline — no external API calls

## ESRS Topics Covered

| Code | Topic | Pillar |
|------|-------|--------|
| E1 | Climate Change | Environmental |
| E2 | Pollution | Environmental |
| E3 | Water & Marine Resources | Environmental |
| S1 | Own Workforce | Social |
| S2 | Workers in Value Chain | Social |
| G1 | Business Conduct | Governance |
| G2 | Corporate Culture & Anti-Corruption | Governance |

## Installation

```bash
git clone https://github.com/wnk8/double-materiality-assessment.git
cd double-materiality-assessment
pip install -r requirements.txt
```

## Usage

```bash
# Step 1: Generate the Excel input template
python main.py generate-template --output data/iro_template.xlsx

# Step 2: Fill in the template, then run the assessment
python main.py run --input data/iro_template.xlsx --company "Muster GmbH" --year 2025
```

Outputs are saved to `outputs/`:
- `outputs/materiality_matrix.png`
- `outputs/esrs_heatmap.png`
- `outputs/dma_report.pdf`

## Methodology

Scoring follows the EFRAG Double Materiality Assessment methodology:

**Impact Materiality (inside-out)**
```
impact_score = (magnitude × 0.4) + (scope × 0.3) + (irremediability × 0.3)
```

**Financial Materiality (outside-in)**
```
financial_score = (likelihood × magnitude) / 5
```

A topic is **doubly material** when both scores are ≥ 3.0.

## License

[GPL v3](LICENSE)
