# CLAUDE.md — Double Materiality Assessment Tool

## Project Overview

A Python-based, CSRD/ESRS-compliant **Double Materiality Assessment (DMA) Tool** for companies required to conduct materiality analyses under the Corporate Sustainability Reporting Directive (CSRD). The tool operationalizes the EFRAG methodology for assessing both Impact Materiality (inside-out) and Financial Materiality (outside-in) across ESRS topics.

**Target users:** Sustainability managers, ESG consultants, compliance officers in DACH-region companies.
**License:** GPL v3 (public GitHub repository)
**Language:** German UI strings where applicable; code and docs in English.

---

## Architecture

```
double-materiality-tool/
├── CLAUDE.md
├── README.md
├── LICENSE (GPL v3)
├── requirements.txt
├── .gitignore
├── main.py                        # CLI entry point
├── config/
│   └── esrs_topics.json           # ESRS topic definitions & IRO catalogue
├── data/
│   └── iro_template.xlsx          # Pre-filled Excel input template (generated)
├── src/
│   ├── __init__.py
│   ├── template_generator.py      # Generates Excel IRO input template
│   ├── data_loader.py             # Reads and validates Excel input
│   ├── scoring_engine.py          # Core DMA scoring logic
│   ├── matrix_generator.py        # Materiality matrix (matplotlib)
│   ├── heatmap_generator.py       # ESRS heatmap (seaborn)
│   └── report_generator.py        # PDF report (ReportLab)
├── outputs/                       # Auto-created; stores all generated files
└── tests/
    ├── test_scoring_engine.py
    └── test_data_loader.py
```

---

## ESRS Domain Model

### Covered ESRS Topics (7)
| Code | Topic | Pillar |
|------|-------|--------|
| E1 | Climate Change | Environmental |
| E2 | Pollution | Environmental |
| E3 | Water & Marine Resources | Environmental |
| S1 | Own Workforce | Social |
| S2 | Workers in Value Chain | Social |
| G1 | Business Conduct | Governance |
| G2 | Corporate Culture & Anti-Corruption | Governance |

### IRO Structure (20 total)
Each IRO (Impact, Risk, Opportunity) has:
- `iro_id`: unique identifier (e.g., E1-I1, E1-R1, E1-O1)
- `esrs_topic`: one of the 7 topics above
- `iro_type`: Impact | Risk | Opportunity
- `description`: plain-language description
- `impact_score`: 1–5 (inside-out; magnitude, scope, irremediability)
- `financial_score`: 1–5 (outside-in; likelihood × magnitude)
- `time_horizon`: short | medium | long
- `is_material`: bool (derived, not user-input)

### Materiality Thresholds (EFRAG methodology)
- **Impact material** if `impact_score >= 3`
- **Financial material** if `financial_score >= 3`
- **Doubly material** if both conditions met

---

## Scoring Engine Logic

```python
# Impact Materiality (inside-out)
# Weighted average of: magnitude (40%), scope (30%), irremediability (30%)
impact_score = (magnitude * 0.4) + (scope * 0.3) + (irremediability * 0.3)

# Financial Materiality (outside-in)
# likelihood × magnitude, normalized to 1–5 scale
financial_score = (likelihood * magnitude) / 5

# Materiality determination
is_impact_material = impact_score >= 3.0
is_financial_material = financial_score >= 3.0
is_doubly_material = is_impact_material and is_financial_material
```

---

## Output Specifications

### 1. Excel IRO Input Template (`data/iro_template.xlsx`)
- Sheet 1: "Instructions" — methodology explanation
- Sheet 2: "IRO_Input" — pre-filled with 20 IROs; user fills scoring columns
- Sheet 3: "ESRS_Reference" — topic descriptions and regulatory references
- Validation: dropdown lists for scores 1–5, time horizons

### 2. Materiality Matrix (`outputs/materiality_matrix.png`)
- X-axis: Financial Materiality Score (1–5)
- Y-axis: Impact Materiality Score (1–5)
- Quadrants: color-coded (grey, orange, red for increasing materiality)
- Each IRO plotted as labeled data point
- Threshold lines at score 3.0 on both axes

### 3. ESRS Heatmap (`outputs/esrs_heatmap.png`)
- Rows: 7 ESRS topics
- Columns: Impact Score | Financial Score | Doubly Material (Yes/No)
- Color gradient: white → dark green (low → high materiality)
- Cell annotations: numeric scores

### 4. PDF Report (`outputs/dma_report.pdf`)
- Page 1: Cover — company name, date, tool version
- Page 2: Executive Summary — materiality counts, methodology note
- Page 3–4: Full IRO table with scores and materiality flags
- Page 5: Embedded materiality matrix image
- Page 6: Embedded ESRS heatmap image
- Page 7: Methodology appendix (EFRAG DMA reference)
- Font: Liberation Serif or fallback to Helvetica
- Color palette: pastel (consistent with ESRS reporting conventions)

---

## Tech Stack

| Component | Library | Version |
|-----------|---------|---------|
| Excel I/O | openpyxl | >=3.1.0 |
| Data processing | pandas | >=2.0.0 |
| Visualization | matplotlib | >=3.7.0 |
| Heatmap | seaborn | >=0.12.0 |
| PDF generation | reportlab | >=4.0.0 |
| CLI | argparse | stdlib |
| Testing | pytest | >=7.0.0 |

---

## CLI Interface

```bash
# Step 1: Generate blank Excel input template
python main.py generate-template --output data/iro_template.xlsx

# Step 2: User fills in the template, then:
python main.py run --input data/iro_template.xlsx --company "Muster GmbH" --year 2025

# Step 3: Outputs auto-saved to outputs/
# outputs/materiality_matrix.png
# outputs/esrs_heatmap.png
# outputs/dma_report.pdf
```

---

## Key Constraints & Decisions

1. **No web framework** — pure CLI tool; no Flask/FastAPI to keep it simple and portable
2. **No database** — Excel in, files out; stateless by design
3. **GPL v3** — fully open source; CV/portfolio visibility
4. **German-friendly** — IRO descriptions and PDF report support German text (UTF-8 throughout)
5. **No external API calls** — fully offline; no dependency on internet connectivity
6. **Reproducible outputs** — same input always produces same output (deterministic)

---

## Development Phases

See sequential build plan in `docs/BUILD_PLAN.md` (generated by Claude Code prompts).

---

## Error Handling Standards

- All file I/O wrapped in try/except with descriptive error messages
- Excel validation errors surface as named exceptions: `InvalidScoreError`, `MissingIROError`
- CLI always exits with code 0 (success) or 1 (error)
- No silent failures

---

## CV Reference Entry

> *"Developed a Python-based CSRD/ESRS-compliant Double Materiality Assessment Tool; assesses 20 IROs across 7 ESRS topics using EFRAG methodology; outputs: Excel IRO template, scoring engine, materiality matrix, ESRS heatmap, and automated PDF report. GPL v3, public GitHub."*
