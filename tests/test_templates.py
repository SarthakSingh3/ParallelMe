"""Unit tests for multi-domain templates and multi-language translations."""

from parallelme.models import Decision
from parallelme.templates_and_i18n import (
    TRANSLATIONS,
    create_decision_from_template,
    get_prebuilt_templates,
)


def test_translations_dictionary_keys():
    for lang in ["EN", "HI", "HING"]:
        assert lang in TRANSLATIONS
        assert "app_title" in TRANSLATIONS[lang]
        assert "tab_simulate" in TRANSLATIONS[lang]


def test_get_prebuilt_templates():
    templates = get_prebuilt_templates()
    assert "trip_planning" in templates
    assert "fitness_health" in templates
    assert "career_study" in templates
    assert "purchase_finance" in templates

    # Check that each template has at least 2 alternative scenarios
    for key, tpl in templates.items():
        assert len(tpl["scenarios"]) >= 2
        assert tpl["time_horizon_weeks"] > 0
        assert tpl["max_weekly_hours"] > 0


def test_create_decision_from_template():
    d = create_decision_from_template("trip_planning", custom_title="My Europe Trip")
    assert d.title == "My Europe Trip"
    assert len(d.scenarios) >= 2
    assert d.time_horizon_weeks == 2

    # Check fallback for unknown template key
    fallback_d = create_decision_from_template("unknown_key")
    assert fallback_d is not None
    assert len(fallback_d.scenarios) >= 2
