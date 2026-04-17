"""Bilingual UI strings — DE / EN."""

STRINGS: dict[str, dict[str, str]] = {
    "de": {
        # App shell
        "title": "Doppelte Wesentlichkeitsanalyse",
        "subtitle": "CSRD / ESRS · EFRAG-Methodik",
        "step_company": "Firma",
        "step_iros": "IRO-Bewertung",
        "step_results": "Ergebnisse",
        # Step 1
        "company_label": "Firmenname",
        "company_placeholder": "z. B. Muster GmbH",
        "year_label": "Berichtsjahr",
        "lang_toggle": "Sprache",
        "next_btn": "Weiter →",
        "error_company": "Bitte Firmennamen eingeben.",
        "error_year": "Bitte ein gültiges Jahr eingeben.",
        # Step 2 — sidebar
        "sidebar_title": "ESRS-Themen",
        "progress_label": "Bewertet",
        "scored_label": "IROs bewertet",
        # Step 2 — IRO form
        "pillar_env": "Umwelt",
        "pillar_soc": "Soziales",
        "pillar_gov": "Governance",
        "type_impact": "Auswirkung",
        "type_risk": "Risiko",
        "type_opp": "Chance",
        "magnitude": "Ausmaß",
        "scope": "Reichweite",
        "irremediability": "Behebbarkeit",
        "likelihood": "Eintrittswahrscheinlichkeit",
        "fin_magnitude": "Finanzielle Auswirkung",
        "time_horizon": "Zeithorizont",
        "time_short": "Kurzfristig (short)",
        "time_medium": "Mittelfristig (medium)",
        "time_long": "Langfristig (long)",
        "live_impact": "Auswirkungsscore",
        "live_financial": "Finanzscore",
        "material_yes": "✅ Wesentlich",
        "material_no": "— Nicht wesentlich",
        "back_btn": "← Zurück",
        "run_btn": "Analyse starten ▶",
        "running": "Analyse wird durchgeführt…",
        # Step 3 — tabs
        "tab_summary": "Zusammenfassung",
        "tab_matrix": "Wesentlichkeitsmatrix",
        "tab_heatmap": "ESRS-Heatmap",
        "tab_table": "IRO-Tabelle",
        # Step 3 — KPIs
        "kpi_total": "IROs gesamt",
        "kpi_impact": "Auswirkungswesentlich",
        "kpi_financial": "Finanziell wesentlich",
        "kpi_doubly": "Doppelt wesentlich",
        # Step 3 — topic table
        "topic_col": "ESRS-Thema",
        "impact_col": "Auswirkungsscore",
        "financial_col": "Finanzscore",
        "doubly_col": "Doppelt wesentlich",
        "yes": "✅ Ja",
        "no": "—",
        # Step 3 — IRO table columns
        "col_id": "IRO-ID",
        "col_topic": "Thema",
        "col_type": "Typ",
        "col_desc": "Beschreibung",
        "col_impact": "Auswirk.",
        "col_fin": "Finanziell",
        "col_amat": "A-wes.",
        "col_fmat": "F-wes.",
        "col_dmat": "D-wes.",
        # Step 3 — downloads
        "dl_pdf": "📄 PDF-Bericht herunterladen",
        "dl_excel": "📊 Excel-Template herunterladen",
        "new_analysis": "← Neue Analyse",
        # Captions
        "matrix_caption": (
            "Abbildung 1: Doppelte Wesentlichkeitsmatrix — "
            "Schwellenwert 3,0 auf beiden Achsen"
        ),
        "heatmap_caption": (
            "Abbildung 2: ESRS-Themenübersicht — "
            "maximale Scores je Thema"
        ),
        # Methodology note
        "method_note": (
            "**Methodik:** Auswirkungsscore = (Ausmaß×0,4) + (Reichweite×0,3) + "
            "(Behebbarkeit×0,3) · Finanzscore = (Likelihood × Fin. Auswirkung) ÷ 5 · "
            "Wesentlich ab Score ≥ 3,0"
        ),
    },
    "en": {
        # App shell
        "title": "Double Materiality Assessment",
        "subtitle": "CSRD / ESRS · EFRAG Methodology",
        "step_company": "Company",
        "step_iros": "IRO Scoring",
        "step_results": "Results",
        # Step 1
        "company_label": "Company name",
        "company_placeholder": "e.g. Example Ltd",
        "year_label": "Reporting year",
        "lang_toggle": "Language",
        "next_btn": "Next →",
        "error_company": "Please enter a company name.",
        "error_year": "Please enter a valid year.",
        # Step 2 — sidebar
        "sidebar_title": "ESRS Topics",
        "progress_label": "Scored",
        "scored_label": "IROs scored",
        # Step 2 — IRO form
        "pillar_env": "Environmental",
        "pillar_soc": "Social",
        "pillar_gov": "Governance",
        "type_impact": "Impact",
        "type_risk": "Risk",
        "type_opp": "Opportunity",
        "magnitude": "Magnitude",
        "scope": "Scope",
        "irremediability": "Irremediability",
        "likelihood": "Likelihood",
        "fin_magnitude": "Financial Magnitude",
        "time_horizon": "Time horizon",
        "time_short": "Short-term (short)",
        "time_medium": "Medium-term (medium)",
        "time_long": "Long-term (long)",
        "live_impact": "Impact score",
        "live_financial": "Financial score",
        "material_yes": "✅ Material",
        "material_no": "— Not material",
        "back_btn": "← Back",
        "run_btn": "Run Assessment ▶",
        "running": "Running assessment…",
        # Step 3 — tabs
        "tab_summary": "Summary",
        "tab_matrix": "Materiality Matrix",
        "tab_heatmap": "ESRS Heatmap",
        "tab_table": "IRO Table",
        # Step 3 — KPIs
        "kpi_total": "Total IROs",
        "kpi_impact": "Impact material",
        "kpi_financial": "Financially material",
        "kpi_doubly": "Doubly material",
        # Step 3 — topic table
        "topic_col": "ESRS Topic",
        "impact_col": "Impact Score",
        "financial_col": "Financial Score",
        "doubly_col": "Doubly Material",
        "yes": "✅ Yes",
        "no": "—",
        # Step 3 — IRO table columns
        "col_id": "IRO-ID",
        "col_topic": "Topic",
        "col_type": "Type",
        "col_desc": "Description",
        "col_impact": "Impact",
        "col_fin": "Financial",
        "col_amat": "I-mat.",
        "col_fmat": "F-mat.",
        "col_dmat": "D-mat.",
        # Step 3 — downloads
        "dl_pdf": "📄 Download PDF Report",
        "dl_excel": "📊 Download Excel Template",
        "new_analysis": "← New Analysis",
        # Captions
        "matrix_caption": (
            "Figure 1: Double Materiality Matrix — "
            "threshold 3.0 on both axes"
        ),
        "heatmap_caption": (
            "Figure 2: ESRS Topic Overview — "
            "maximum scores per topic"
        ),
        # Methodology note
        "method_note": (
            "**Methodology:** Impact score = (Magnitude×0.4) + (Scope×0.3) + "
            "(Irremediability×0.3) · Financial score = (Likelihood × Fin. Magnitude) ÷ 5 · "
            "Material if score ≥ 3.0"
        ),
    },
}

TOPIC_NAMES: dict[str, dict[str, str]] = {
    "de": {
        "E1": "Klimawandel",
        "E2": "Umweltverschmutzung",
        "E3": "Wasser & Meeresressourcen",
        "S1": "Eigene Belegschaft",
        "S2": "Arbeitskräfte in der Lieferkette",
        "G1": "Unternehmensführung",
        "G2": "Unternehmenskultur & Antikorruption",
    },
    "en": {
        "E1": "Climate Change",
        "E2": "Pollution",
        "E3": "Water & Marine Resources",
        "S1": "Own Workforce",
        "S2": "Workers in Value Chain",
        "G1": "Business Conduct",
        "G2": "Corporate Culture & Anti-Corruption",
    },
}

PILLAR_MAP: dict[str, str] = {
    "E1": "Environmental",
    "E2": "Environmental",
    "E3": "Environmental",
    "S1": "Social",
    "S2": "Social",
    "G1": "Governance",
    "G2": "Governance",
}


def t(key: str, lang: str) -> str:
    """Return translated UI string."""
    return STRINGS.get(lang, STRINGS["de"]).get(key, key)


def topic_name(code: str, lang: str) -> str:
    """Return translated topic name."""
    return TOPIC_NAMES.get(lang, TOPIC_NAMES["de"]).get(code, code)


def pillar_label(code: str, lang: str) -> str:
    """Return translated pillar label."""
    pillar = PILLAR_MAP.get(code, "")
    mapping = {
        "Environmental": t("pillar_env", lang),
        "Social": t("pillar_soc", lang),
        "Governance": t("pillar_gov", lang),
    }
    return mapping.get(pillar, pillar)


def type_label(iro_type: str, lang: str) -> str:
    """Return translated IRO type label."""
    mapping = {
        "Impact": t("type_impact", lang),
        "Risk": t("type_risk", lang),
        "Opportunity": t("type_opp", lang),
    }
    return mapping.get(iro_type, iro_type)
