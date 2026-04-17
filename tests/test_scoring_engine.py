"""Tests for src/scoring_engine.py"""
import pytest
from src.scoring_engine import score_iros, aggregate_by_topic, IMPACT_THRESHOLD, FINANCIAL_THRESHOLD


def make_iro(iro_id="E1-I1", esrs_topic="E1", iro_type="Impact",
             magnitude=3, scope=3, irremediability=3,
             likelihood=3, fin_magnitude=3, time_horizon="medium"):
    return {
        "iro_id": iro_id,
        "esrs_topic": esrs_topic,
        "iro_type": iro_type,
        "description": "Test IRO",
        "magnitude": magnitude,
        "scope": scope,
        "irremediability": irremediability,
        "likelihood": likelihood,
        "fin_magnitude": fin_magnitude,
        "time_horizon": time_horizon,
    }


class TestImpactScore:
    def test_formula_weighted_average(self):
        iro = make_iro(magnitude=4, scope=2, irremediability=3)
        result = score_iros([iro])[0]
        expected = (4 * 0.4) + (2 * 0.3) + (3 * 0.3)  # 1.6 + 0.6 + 0.9 = 3.1
        assert result["impact_score"] == round(expected, 2)

    def test_all_ones_gives_one(self):
        iro = make_iro(magnitude=1, scope=1, irremediability=1)
        result = score_iros([iro])[0]
        assert result["impact_score"] == 1.0

    def test_all_fives_gives_five(self):
        iro = make_iro(magnitude=5, scope=5, irremediability=5)
        result = score_iros([iro])[0]
        assert result["impact_score"] == 5.0


class TestFinancialScore:
    def test_formula_likelihood_times_magnitude_over_five(self):
        iro = make_iro(likelihood=4, fin_magnitude=5)
        result = score_iros([iro])[0]
        expected = (4 * 5) / 5  # 4.0
        assert result["financial_score"] == round(expected, 2)

    def test_min_values_give_low_score(self):
        iro = make_iro(likelihood=1, fin_magnitude=1)
        result = score_iros([iro])[0]
        assert result["financial_score"] == 0.2

    def test_max_values_give_five(self):
        iro = make_iro(likelihood=5, fin_magnitude=5)
        result = score_iros([iro])[0]
        assert result["financial_score"] == 5.0


class TestMaterialityThresholds:
    def test_below_threshold_not_material(self):
        # impact_score = (2*0.4)+(2*0.3)+(2*0.3) = 2.0 < 3.0
        iro = make_iro(magnitude=2, scope=2, irremediability=2,
                       likelihood=2, fin_magnitude=2)
        result = score_iros([iro])[0]
        assert not result["is_impact_material"]
        assert not result["is_financial_material"]
        assert not result["is_doubly_material"]

    def test_exactly_at_threshold_is_material(self):
        # Need impact_score == 3.0 exactly
        # (3*0.4)+(3*0.3)+(3*0.3) = 1.2+0.9+0.9 = 3.0
        # (3*3)/5 = 1.8 — financial NOT material, keep separate
        iro = make_iro(magnitude=3, scope=3, irremediability=3,
                       likelihood=5, fin_magnitude=3)
        result = score_iros([iro])[0]
        assert result["impact_score"] == 3.0
        assert result["is_impact_material"]

    def test_just_below_threshold_not_material(self):
        # impact_score ≈ 2.9: magnitude=3,scope=3,irremediability=2
        # (3*0.4)+(3*0.3)+(2*0.3) = 1.2+0.9+0.6 = 2.7 < 3.0
        iro = make_iro(magnitude=3, scope=3, irremediability=2,
                       likelihood=1, fin_magnitude=1)
        result = score_iros([iro])[0]
        assert not result["is_impact_material"]

    def test_doubly_material_when_both_exceed_threshold(self):
        # impact: (5*0.4)+(5*0.3)+(5*0.3) = 5.0 >= 3.0
        # financial: (5*5)/5 = 5.0 >= 3.0
        iro = make_iro(magnitude=5, scope=5, irremediability=5,
                       likelihood=5, fin_magnitude=5)
        result = score_iros([iro])[0]
        assert result["is_doubly_material"]

    def test_not_doubly_material_when_only_impact(self):
        # impact high, financial low
        iro = make_iro(magnitude=5, scope=5, irremediability=5,
                       likelihood=1, fin_magnitude=1)
        result = score_iros([iro])[0]
        assert result["is_impact_material"]
        assert not result["is_financial_material"]
        assert not result["is_doubly_material"]


class TestAggregateByTopic:
    def test_returns_all_topics_present(self):
        iros = [
            make_iro(iro_id="E1-I1", esrs_topic="E1"),
            make_iro(iro_id="S1-I1", esrs_topic="S1"),
        ]
        scored = score_iros(iros)
        result = aggregate_by_topic(scored)
        assert "E1" in result
        assert "S1" in result

    def test_max_impact_is_highest_across_iros(self):
        iros = [
            make_iro(iro_id="E1-I1", esrs_topic="E1", magnitude=5, scope=5, irremediability=5),
            make_iro(iro_id="E1-I2", esrs_topic="E1", magnitude=1, scope=1, irremediability=1),
        ]
        scored = score_iros(iros)
        result = aggregate_by_topic(scored)
        assert result["E1"]["max_impact"] == 5.0

    def test_doubly_material_true_if_any_iro_qualifies(self):
        iros = [
            make_iro(iro_id="E1-I1", esrs_topic="E1",
                     magnitude=5, scope=5, irremediability=5,
                     likelihood=5, fin_magnitude=5),
            make_iro(iro_id="E1-I2", esrs_topic="E1",
                     magnitude=1, scope=1, irremediability=1,
                     likelihood=1, fin_magnitude=1),
        ]
        scored = score_iros(iros)
        result = aggregate_by_topic(scored)
        assert result["E1"]["doubly_material"] is True

    def test_doubly_material_false_if_no_iro_qualifies(self):
        iros = [
            make_iro(iro_id="E1-I1", esrs_topic="E1",
                     magnitude=1, scope=1, irremediability=1,
                     likelihood=1, fin_magnitude=1),
        ]
        scored = score_iros(iros)
        result = aggregate_by_topic(scored)
        assert result["E1"]["doubly_material"] is False
