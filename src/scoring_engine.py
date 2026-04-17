"""
Scoring Engine — EFRAG Double Materiality Assessment methodology.

Impact Materiality (inside-out):
    impact_score = (magnitude * 0.4) + (scope * 0.3) + (irremediability * 0.3)

Financial Materiality (outside-in):
    financial_score = (likelihood * fin_magnitude) / 5

Thresholds:
    impact_material    if impact_score    >= 3.0
    financial_material if financial_score >= 3.0
    doubly_material    if both conditions met
"""

IMPACT_THRESHOLD = 3.0
FINANCIAL_THRESHOLD = 3.0


def score_iros(iros: list[dict]) -> list[dict]:
    """
    Apply EFRAG scoring formulas to a list of IRO dicts.

    Each input dict must contain:
        magnitude, scope, irremediability, likelihood, fin_magnitude (all 1–5 ints)

    Returns a new list of dicts with added fields:
        impact_score, financial_score,
        is_impact_material, is_financial_material, is_doubly_material
    """
    scored = []
    for iro in iros:
        result = dict(iro)

        magnitude = float(iro["magnitude"])
        scope = float(iro["scope"])
        irremediability = float(iro["irremediability"])
        likelihood = float(iro["likelihood"])
        fin_magnitude = float(iro["fin_magnitude"])

        impact_score = (magnitude * 0.4) + (scope * 0.3) + (irremediability * 0.3)
        financial_score = (likelihood * fin_magnitude) / 5.0

        result["impact_score"] = round(impact_score, 2)
        result["financial_score"] = round(financial_score, 2)
        result["is_impact_material"] = impact_score >= IMPACT_THRESHOLD
        result["is_financial_material"] = financial_score >= FINANCIAL_THRESHOLD
        result["is_doubly_material"] = (
            result["is_impact_material"] and result["is_financial_material"]
        )

        scored.append(result)

    return scored


def aggregate_by_topic(scored_iros: list[dict]) -> dict:
    """
    Aggregate scored IROs by ESRS topic.

    Returns a dict keyed by topic code, e.g.:
        {
            "E1": {
                "max_impact": 4.2,
                "max_financial": 3.8,
                "doubly_material": True
            },
            ...
        }
    """
    topics: dict[str, dict] = {}

    for iro in scored_iros:
        topic = iro["esrs_topic"]
        if topic not in topics:
            topics[topic] = {
                "max_impact": 0.0,
                "max_financial": 0.0,
                "doubly_material": False,
            }

        if iro["impact_score"] > topics[topic]["max_impact"]:
            topics[topic]["max_impact"] = iro["impact_score"]

        if iro["financial_score"] > topics[topic]["max_financial"]:
            topics[topic]["max_financial"] = iro["financial_score"]

        if iro["is_doubly_material"]:
            topics[topic]["doubly_material"] = True

    return topics
