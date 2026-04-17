"""
Double Materiality Assessment Tool — Streamlit Web Interface.

Launch:
    streamlit run app.py
"""

import json
import os
import tempfile

import streamlit as st

from src.i18n import t, topic_name, pillar_label, type_label, PILLAR_MAP
from src.scoring_engine import score_iros, aggregate_by_topic

# ── Constants ─────────────────────────────────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "esrs_topics.json")
TOPIC_ORDER = ["E1", "E2", "E3", "S1", "S2", "G1", "G2"]
TIME_HORIZONS = ["short", "medium", "long"]

PILLAR_COLORS = {
    "Environmental": "#2E7D32",
    "Social": "#1565C0",
    "Governance": "#6A1B9A",
}
TYPE_COLORS = {
    "Impact": "#1565C0",
    "Risk": "#E65100",
    "Opportunity": "#2E7D32",
}
TYPE_BG = {
    "Impact": "#E3F2FD",
    "Risk": "#FFF3E0",
    "Opportunity": "#E8F5E9",
}


# ── Config loader (cached) ────────────────────────────────────────────────────
@st.cache_data
def load_config() -> list[dict]:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)["topics"]


# ── Session state init ────────────────────────────────────────────────────────
def init_state() -> None:
    defaults = {
        "step": 1,
        "lang": "de",
        "company": "",
        "year": 2025,
        "scores": {},
        "scored_iros": [],
        "aggregates": {},
        "matrix_bytes": None,
        "heatmap_bytes": None,
        "pdf_bytes": None,
        "excel_bytes": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ── Progress bar ──────────────────────────────────────────────────────────────
def render_progress(lang: str) -> None:
    steps = [
        t("step_company", lang),
        t("step_iros", lang),
        t("step_results", lang),
    ]
    current = st.session_state.step
    cols = st.columns(len(steps) * 2 - 1)
    for i, label in enumerate(steps):
        col = cols[i * 2]
        if i + 1 < current:
            col.markdown(
                f"<div style='text-align:center;color:#2E7D32;font-weight:600'>"
                f"✓ {label}</div>",
                unsafe_allow_html=True,
            )
        elif i + 1 == current:
            col.markdown(
                f"<div style='text-align:center;color:#1565C0;font-weight:700;"
                f"border-bottom:2px solid #1565C0;padding-bottom:4px'>"
                f"{i+1}. {label}</div>",
                unsafe_allow_html=True,
            )
        else:
            col.markdown(
                f"<div style='text-align:center;color:#9E9E9E'>{i+1}. {label}</div>",
                unsafe_allow_html=True,
            )
        if i < len(steps) - 1:
            cols[i * 2 + 1].markdown(
                "<div style='text-align:center;color:#BDBDBD;padding-top:2px'>──</div>",
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)


# ── Language toggle ───────────────────────────────────────────────────────────
def render_lang_toggle() -> None:
    col1, col2 = st.columns([8, 2])
    with col2:
        lang = st.radio(
            "",
            options=["de", "en"],
            format_func=lambda x: "🇩🇪 DE" if x == "de" else "🇬🇧 EN",
            index=0 if st.session_state.lang == "de" else 1,
            horizontal=True,
            key="lang_radio",
            label_visibility="collapsed",
        )
        if lang != st.session_state.lang:
            st.session_state.lang = lang
            st.rerun()


# ── STEP 1 ────────────────────────────────────────────────────────────────────
def step1() -> None:
    lang = st.session_state.lang
    render_lang_toggle()

    st.markdown(
        f"<h1 style='text-align:center;color:#1F4E79'>{t('title', lang)}</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align:center;color:#607D8B;margin-top:-12px'>"
        f"{t('subtitle', lang)}</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    render_progress(lang)

    # Centred card
    _, col, _ = st.columns([1, 2, 1])
    with col:
        company = st.text_input(
            t("company_label", lang),
            value=st.session_state.company,
            placeholder=t("company_placeholder", lang),
        )
        year = st.number_input(
            t("year_label", lang),
            min_value=2020,
            max_value=2035,
            value=st.session_state.year,
            step=1,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(t("next_btn", lang), use_container_width=True, type="primary"):
            if not company.strip():
                st.error(t("error_company", lang))
            else:
                st.session_state.company = company.strip()
                st.session_state.year = int(year)
                st.session_state.step = 2
                st.rerun()


# ── Helpers for Step 2 ────────────────────────────────────────────────────────
def _live_score(scores: dict) -> tuple[float, float]:
    mag = scores.get("magnitude", 3)
    sco = scores.get("scope", 3)
    irr = scores.get("irremediability", 3)
    lik = scores.get("likelihood", 3)
    fin = scores.get("fin_magnitude", 3)
    impact = (mag * 0.4) + (sco * 0.3) + (irr * 0.3)
    financial = (lik * fin) / 5.0
    return round(impact, 2), round(financial, 2)


def _score_bar(score: float) -> str:
    filled = int(round(score / 5 * 10))
    bar = "█" * filled + "░" * (10 - filled)
    return bar


def _count_scored(scores: dict, topics: list) -> int:
    total = sum(len(topic["iros"]) for topic in topics)
    scored = sum(
        1
        for topic in topics
        for iro in topic["iros"]
        if iro["iro_id"] in scores
        and all(
            scores[iro["iro_id"]].get(f) is not None
            for f in ["magnitude", "scope", "irremediability", "likelihood", "fin_magnitude", "time_horizon"]
        )
    )
    return scored


# ── STEP 2 ────────────────────────────────────────────────────────────────────
def step2() -> None:
    lang = st.session_state.lang
    topics = load_config()
    scores = st.session_state.scores

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            f"**{t('sidebar_title', lang)}**",
            unsafe_allow_html=False,
        )
        st.markdown("---")
        for topic in topics:
            code = topic["code"]
            pillar = PILLAR_MAP.get(code, "")
            color = PILLAR_COLORS.get(pillar, "#555")
            n_iros = len(topic["iros"])
            n_scored = sum(
                1 for iro in topic["iros"]
                if iro["iro_id"] in scores
            )
            check = "✓ " if n_scored == n_iros else ""
            st.markdown(
                f"<a href='#{code.lower()}-anchor' style='text-decoration:none'>"
                f"<div style='padding:4px 8px;margin:2px 0;border-left:3px solid {color};"
                f"color:#333;font-size:13px'>{check}<b>{code}</b> — "
                f"{topic_name(code, lang)}"
                f"<span style='color:#999;font-size:11px;float:right'>"
                f"{n_scored}/{n_iros}</span></div></a>",
                unsafe_allow_html=True,
            )
        st.markdown("---")
        n_scored_total = _count_scored(scores, topics)
        n_total = sum(len(t_["iros"]) for t_ in topics)
        st.progress(n_scored_total / n_total if n_total else 0)
        st.caption(f"{n_scored_total} / {n_total} {t('scored_label', lang)}")

    # ── Header ───────────────────────────────────────────────────────────────
    render_lang_toggle()
    render_progress(lang)

    st.markdown(
        f"<h2 style='color:#1F4E79'>{t('step_iros', lang)}</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(t("method_note", lang))
    st.markdown("<br>", unsafe_allow_html=True)

    # ── IRO cards per topic ───────────────────────────────────────────────────
    for topic in topics:
        code = topic["code"]
        pillar = PILLAR_MAP.get(code, "")
        p_color = PILLAR_COLORS.get(pillar, "#555")
        p_label = pillar_label(code, lang)
        t_name = topic_name(code, lang)

        # Anchor for sidebar links
        st.markdown(
            f"<div id='{code.lower()}-anchor'></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:10px;margin:16px 0 8px'>"
            f"<span style='font-size:20px;font-weight:700;color:#1F4E79'>{code}</span>"
            f"<span style='font-size:16px;font-weight:600;color:#333'>{t_name}</span>"
            f"<span style='background:{p_color};color:white;padding:2px 8px;"
            f"border-radius:12px;font-size:11px'>{p_label}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        for iro in topic["iros"]:
            iro_id = iro["iro_id"]
            iro_type = iro["iro_type"]
            t_color = TYPE_COLORS.get(iro_type, "#555")
            t_bg = TYPE_BG.get(iro_type, "#F5F5F5")
            t_lbl = type_label(iro_type, lang)

            if iro_id not in scores:
                scores[iro_id] = {
                    "magnitude": 3, "scope": 3, "irremediability": 3,
                    "likelihood": 3, "fin_magnitude": 3, "time_horizon": "medium"
                }

            with st.expander(
                f"**{iro_id}** — {iro['description'][:80]}{'…' if len(iro['description']) > 80 else ''}",
                expanded=False,
            ):
                # Type badge + description
                st.markdown(
                    f"<span style='background:{t_bg};color:{t_color};"
                    f"padding:2px 8px;border-radius:10px;font-size:11px;"
                    f"font-weight:600'>{t_lbl}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p style='color:#607D8B;font-style:italic;margin:6px 0 12px'>"
                    f"{iro['description']}</p>",
                    unsafe_allow_html=True,
                )

                col_impact, col_fin = st.columns(2)

                with col_impact:
                    st.markdown(f"**{t('impact_score', lang)}**" if lang == "de" else "**Impact scoring**")
                    scores[iro_id]["magnitude"] = st.slider(
                        t("magnitude", lang),
                        1, 5,
                        value=scores[iro_id]["magnitude"],
                        key=f"{iro_id}_mag",
                    )
                    scores[iro_id]["scope"] = st.slider(
                        t("scope", lang),
                        1, 5,
                        value=scores[iro_id]["scope"],
                        key=f"{iro_id}_sco",
                    )
                    scores[iro_id]["irremediability"] = st.slider(
                        t("irremediability", lang),
                        1, 5,
                        value=scores[iro_id]["irremediability"],
                        key=f"{iro_id}_irr",
                    )

                with col_fin:
                    st.markdown(f"**{t('financial_score', lang)}**" if lang == "de" else "**Financial scoring**")
                    scores[iro_id]["likelihood"] = st.slider(
                        t("likelihood", lang),
                        1, 5,
                        value=scores[iro_id]["likelihood"],
                        key=f"{iro_id}_lik",
                    )
                    scores[iro_id]["fin_magnitude"] = st.slider(
                        t("fin_magnitude", lang),
                        1, 5,
                        value=scores[iro_id]["fin_magnitude"],
                        key=f"{iro_id}_fin",
                    )
                    scores[iro_id]["time_horizon"] = st.selectbox(
                        t("time_horizon", lang),
                        options=TIME_HORIZONS,
                        format_func=lambda x: {
                            "short": t("time_short", lang),
                            "medium": t("time_medium", lang),
                            "long": t("time_long", lang),
                        }[x],
                        index=TIME_HORIZONS.index(scores[iro_id]["time_horizon"]),
                        key=f"{iro_id}_hor",
                    )

                # Live score preview
                imp, fin = _live_score(scores[iro_id])
                imp_bar = _score_bar(imp)
                fin_bar = _score_bar(fin)
                imp_mat = imp >= 3.0
                fin_mat = fin >= 3.0
                imp_status = t("material_yes", lang) if imp_mat else t("material_no", lang)
                fin_status = t("material_yes", lang) if fin_mat else t("material_no", lang)
                imp_color = "#2E7D32" if imp_mat else "#9E9E9E"
                fin_color = "#2E7D32" if fin_mat else "#9E9E9E"

                st.markdown(
                    f"<div style='background:#F8F9FA;border-radius:8px;padding:10px 14px;"
                    f"margin-top:10px;font-family:monospace;font-size:13px'>"
                    f"<div><b style='color:#1F4E79'>{t('live_impact', lang)}:</b> "
                    f"<b>{imp:.2f}</b>  {imp_bar}  "
                    f"<span style='color:{imp_color}'>{imp_status}</span></div>"
                    f"<div style='margin-top:4px'><b style='color:#1F4E79'>"
                    f"{t('live_financial', lang)}:</b> "
                    f"<b>{fin:.2f}</b>  {fin_bar}  "
                    f"<span style='color:{fin_color}'>{fin_status}</span></div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("---")

    st.session_state.scores = scores

    # ── Navigation ────────────────────────────────────────────────────────────
    col_back, _, col_run = st.columns([2, 3, 2])
    with col_back:
        if st.button(t("back_btn", lang), use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    with col_run:
        if st.button(t("run_btn", lang), use_container_width=True, type="primary"):
            _run_analysis(lang, topics)


def _run_analysis(lang: str, topics: list) -> None:
    """Build IRO list from session scores, run scoring, generate outputs."""
    scores = st.session_state.scores

    # Build flat IRO list (same structure data_loader returns)
    iros = []
    for topic in topics:
        code = topic["code"]
        for iro in topic["iros"]:
            iro_id = iro["iro_id"]
            s = scores.get(iro_id, {})
            iros.append({
                "iro_id": iro_id,
                "esrs_topic": code,
                "iro_type": iro["iro_type"],
                "description": iro["description"],
                "magnitude": s.get("magnitude", 3),
                "scope": s.get("scope", 3),
                "irremediability": s.get("irremediability", 3),
                "likelihood": s.get("likelihood", 3),
                "fin_magnitude": s.get("fin_magnitude", 3),
                "time_horizon": s.get("time_horizon", "medium"),
            })

    with st.spinner(t("running", lang)):
        scored = score_iros(iros)
        aggregates = aggregate_by_topic(scored)

        # Generate outputs to temp files
        with tempfile.TemporaryDirectory() as tmpdir:
            matrix_path = os.path.join(tmpdir, "materiality_matrix.png")
            heatmap_path = os.path.join(tmpdir, "esrs_heatmap.png")
            report_path = os.path.join(tmpdir, "dma_report.pdf")
            excel_path = os.path.join(tmpdir, "iro_template.xlsx")

            from src.matrix_generator import generate_matrix
            from src.heatmap_generator import generate_heatmap
            from src.report_generator import generate_report
            from src.template_generator import generate_template

            generate_matrix(scored, matrix_path)
            generate_heatmap(aggregates, heatmap_path)
            generate_report(
                scored_iros=scored,
                topic_aggregates=aggregates,
                company=st.session_state.company,
                year=st.session_state.year,
                matrix_path=matrix_path,
                heatmap_path=heatmap_path,
                output_path=report_path,
            )
            generate_template(excel_path)

            # Read bytes while tmpdir still exists
            with open(matrix_path, "rb") as f:
                st.session_state.matrix_bytes = f.read()
            with open(heatmap_path, "rb") as f:
                st.session_state.heatmap_bytes = f.read()
            with open(report_path, "rb") as f:
                st.session_state.pdf_bytes = f.read()
            with open(excel_path, "rb") as f:
                st.session_state.excel_bytes = f.read()

    st.session_state.scored_iros = scored
    st.session_state.aggregates = aggregates
    st.session_state.step = 3
    st.rerun()


# ── STEP 3 ────────────────────────────────────────────────────────────────────
def step3() -> None:
    lang = st.session_state.lang
    scored = st.session_state.scored_iros
    aggregates = st.session_state.aggregates

    # ── Sidebar downloads ─────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"**{st.session_state.company}** — {st.session_state.year}")
        st.markdown("---")
        if st.session_state.pdf_bytes:
            st.download_button(
                label=t("dl_pdf", lang),
                data=st.session_state.pdf_bytes,
                file_name="dma_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        if st.session_state.excel_bytes:
            st.download_button(
                label=t("dl_excel", lang),
                data=st.session_state.excel_bytes,
                file_name="iro_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        st.markdown("---")
        if st.button(t("new_analysis", lang), use_container_width=True):
            for key in ["step", "company", "year", "scores", "scored_iros",
                        "aggregates", "matrix_bytes", "heatmap_bytes",
                        "pdf_bytes", "excel_bytes"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # ── Header ───────────────────────────────────────────────────────────────
    render_lang_toggle()
    render_progress(lang)

    st.markdown(
        f"<h2 style='color:#1F4E79'>{t('step_results', lang)} — "
        f"{st.session_state.company} {st.session_state.year}</h2>",
        unsafe_allow_html=True,
    )

    # ── KPI metrics ───────────────────────────────────────────────────────────
    n_total = len(scored)
    n_impact = sum(1 for i in scored if i["is_impact_material"])
    n_fin = sum(1 for i in scored if i["is_financial_material"])
    n_doubly = sum(1 for i in scored if i["is_doubly_material"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("kpi_total", lang), n_total)
    c2.metric(t("kpi_impact", lang), n_impact)
    c3.metric(t("kpi_financial", lang), n_fin)
    c4.metric(
        t("kpi_doubly", lang),
        n_doubly,
        delta=f"{'⚠' if n_doubly > 0 else ''}",
        delta_color="inverse" if n_doubly > 0 else "off",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab_sum, tab_mat, tab_heat, tab_tbl = st.tabs([
        t("tab_summary", lang),
        t("tab_matrix", lang),
        t("tab_heatmap", lang),
        t("tab_table", lang),
    ])

    # Tab 1 — Summary
    with tab_sum:
        st.markdown(f"#### {t('tab_summary', lang)}")
        import pandas as pd

        topic_rows = []
        for code in TOPIC_ORDER:
            agg = aggregates.get(code, {})
            topic_rows.append({
                t("topic_col", lang): f"{code} — {topic_name(code, lang)}",
                t("impact_col", lang): f"{agg.get('max_impact', 0):.2f}",
                t("financial_col", lang): f"{agg.get('max_financial', 0):.2f}",
                t("doubly_col", lang): t("yes", lang) if agg.get("doubly_material") else t("no", lang),
            })

        df_topics = pd.DataFrame(topic_rows)

        def _highlight_doubly(row):
            doubly_col = t("doubly_col", lang)
            if row[doubly_col] == t("yes", lang):
                return ["background-color: #FFCDD2"] * len(row)
            return [""] * len(row)

        st.dataframe(
            df_topics.style.apply(_highlight_doubly, axis=1),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown(t("method_note", lang))

    # Tab 2 — Matrix
    with tab_mat:
        if st.session_state.matrix_bytes:
            st.image(st.session_state.matrix_bytes, use_container_width=True)
            st.caption(t("matrix_caption", lang))

    # Tab 3 — Heatmap
    with tab_heat:
        if st.session_state.heatmap_bytes:
            st.image(st.session_state.heatmap_bytes, use_container_width=True)
            st.caption(t("heatmap_caption", lang))

    # Tab 4 — IRO Table
    with tab_tbl:
        import pandas as pd

        rows = []
        for iro in scored:
            rows.append({
                t("col_id", lang): iro["iro_id"],
                t("col_topic", lang): iro["esrs_topic"],
                t("col_type", lang): type_label(iro["iro_type"], lang),
                t("col_desc", lang): iro["description"][:60] + "…",
                t("col_impact", lang): f"{iro['impact_score']:.2f}",
                t("col_fin", lang): f"{iro['financial_score']:.2f}",
                t("col_amat", lang): "✓" if iro["is_impact_material"] else "—",
                t("col_fmat", lang): "✓" if iro["is_financial_material"] else "—",
                t("col_dmat", lang): "✓" if iro["is_doubly_material"] else "—",
            })

        df_iros = pd.DataFrame(rows)

        def _highlight_iro(row):
            dmat_col = t("col_dmat", lang)
            amat_col = t("col_amat", lang)
            fmat_col = t("col_fmat", lang)
            if row[dmat_col] == "✓":
                return ["background-color: #FFCDD2"] * len(row)
            if row[amat_col] == "✓" or row[fmat_col] == "✓":
                return ["background-color: #FFE0B2"] * len(row)
            return [""] * len(row)

        st.dataframe(
            df_iros.style.apply(_highlight_iro, axis=1),
            use_container_width=True,
            hide_index=True,
        )

    # ── Bottom download bar ───────────────────────────────────────────────────
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.session_state.pdf_bytes:
            st.download_button(
                label=t("dl_pdf", lang),
                data=st.session_state.pdf_bytes,
                file_name="dma_report.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )
    with col2:
        if st.session_state.excel_bytes:
            st.download_button(
                label=t("dl_excel", lang),
                data=st.session_state.excel_bytes,
                file_name="iro_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
    with col3:
        if st.button(t("new_analysis", lang), use_container_width=True):
            for key in ["step", "company", "year", "scores", "scored_iros",
                        "aggregates", "matrix_bytes", "heatmap_bytes",
                        "pdf_bytes", "excel_bytes"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    st.set_page_config(
        page_title="Double Materiality Assessment",
        page_icon="🌿",
        layout="wide",
        initial_sidebar_state="auto",
    )

    # Minimal custom CSS
    st.markdown(
        """
        <style>
        .stApp { background-color: #FAFAFA; }
        .stExpander > summary { font-size: 14px; }
        div[data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    init_state()

    step = st.session_state.step
    if step == 1:
        step1()
    elif step == 2:
        step2()
    elif step == 3:
        step3()


if __name__ == "__main__":
    main()
