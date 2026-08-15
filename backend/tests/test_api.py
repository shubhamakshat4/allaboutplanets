"""API contract, determinism, error handling and no-interpretation audit."""
import pytest
from fastapi.testclient import TestClient

from app.astrology.rules import planetary_rules as pr
from app.main import app

client = TestClient(app)

VALID = {
    "year": 1990, "month": 5, "day": 15,
    "hour": 10, "minute": 30, "second": 0,
    "place_name": "Chennai, India",
    "latitude": 13.0827, "longitude": 80.2707,
    "utc_offset_hours": 5.5,
    "ayanamsha_mode": "LAHIRI",
}


@pytest.fixture(scope="module")
def chart():
    response = client.post("/api/chart", json=VALID)
    assert response.status_code == 200, response.text
    return response.json()


# --- Health and metadata ---------------------------------------------------
def test_health():
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["pyjhora_version"]


def test_meta_exposes_configuration():
    body = client.get("/api/meta").json()
    assert body["pyjhora_version"]
    assert body["default_ayanamsha"] == "LAHIRI"
    assert len(body["planets"]) == 9
    assert len(body["varga_factors"]) == 16
    assert body["pyjhora_yoga_module"]["used"] is False


def test_rules_endpoint_documents_every_rule():
    rules = client.get("/api/rules").json()["rules"]
    ids = {r["rule_id"] for r in rules}
    for required in ("KUMARADI_001", "CHAITANYADI_001", "MAITRI_001", "MAITRI_002",
                     "MAITRI_003", "DIGNITY_001", "DIGNITY_002", "VARGA_001",
                     "HOUSE_001", "NB_100", "BENEFIC_001", "DISPOSITOR_001"):
        assert required in ids
    for n in range(1, 23):
        assert f"YOGA_{n:03d}" in ids
    for r in rules:
        assert r["name"] and r["description"] and r["source"]


# --- Chart -----------------------------------------------------------------
def test_chart_shape(chart):
    assert chart["chart_id"]
    assert len(chart["planets"]) == 9
    assert len(chart["houses"]) == 12
    assert len(chart["yogas"]) == 22
    assert chart["settings"]["ayanamsha_mode"] == "LAHIRI"
    assert chart["settings"]["zodiac_type"] == "Sidereal (Nirayana)"
    assert chart["settings"]["pyjhora_version"]
    assert chart["birth"]["utc_offset_label"] == "UTC+05:30"
    assert chart["birth"]["date_label"] == "15/05/1990"
    assert chart["birth"]["time_label"] == "10:30:00"


def test_chart_is_deterministic():
    """The same birth details must always produce the same id and numbers."""
    first = client.post("/api/chart", json=VALID).json()
    second = client.post("/api/chart", json=VALID).json()
    assert first["chart_id"] == second["chart_id"]
    assert first["planets"] == second["planets"]
    assert first["yogas"] == second["yogas"]
    assert first["settings"]["ayanamsha_value"] == second["settings"]["ayanamsha_value"]


def test_chart_survives_a_server_restart_by_being_reproducible():
    """The frontend recovers a retired chart by re-posting the birth details.

    That only works if a rebuilt chart is byte-identical and keeps the same id,
    so this asserts the property directly by clearing the server cache the way
    a restart or an LRU eviction would.
    """
    from app.api import routes

    first = client.post("/api/chart", json=VALID).json()
    chart_id = first["chart_id"]
    assert client.get(f"/api/chart/{chart_id}/planet/4").status_code == 200

    # Simulate the process restarting: every cached chart is gone.
    with routes._cache_lock:
        routes._cache.clear()
        routes._cache_meta.clear()

    stale = client.get(f"/api/chart/{chart_id}/planet/4")
    assert stale.status_code == 404
    assert "no longer held on the server" in stale.json()["detail"]

    # Re-posting the same details must reproduce the identical chart.
    rebuilt = client.post("/api/chart", json=VALID).json()
    assert rebuilt["chart_id"] == chart_id
    assert rebuilt["planets"] == first["planets"]
    assert rebuilt["yogas"] == first["yogas"]
    assert rebuilt["houses"] == first["houses"]
    assert rebuilt["settings"] == first["settings"]
    assert rebuilt["birth"] == first["birth"]

    # And the analysis the user originally asked for now resolves.
    assert client.get(f"/api/chart/{chart_id}/planet/4").status_code == 200


def test_evicted_chart_reports_the_recoverable_404_message():
    """The frontend keys its transparent retry off this exact wording, so an
    unknown planet id must NOT carry it."""
    chart_id = client.post("/api/chart", json=VALID).json()["chart_id"]

    missing_chart = client.get("/api/chart/ffffffffffffffffffff/planet/4")
    assert missing_chart.status_code == 404
    assert "no longer held on the server" in missing_chart.json()["detail"]

    missing_planet = client.get(f"/api/chart/{chart_id}/planet/99")
    assert missing_planet.status_code == 404
    assert "no longer held on the server" not in missing_planet.json()["detail"]


def test_different_ayanamsha_gives_a_different_chart():
    other = client.post("/api/chart", json={**VALID, "ayanamsha_mode": "RAMAN"}).json()
    base = client.post("/api/chart", json=VALID).json()
    assert other["chart_id"] != base["chart_id"]
    assert other["settings"]["ayanamsha_value"] != base["settings"]["ayanamsha_value"]


def test_timezone_by_iana_name_matches_explicit_offset():
    payload = {k: v for k, v in VALID.items() if k != "utc_offset_hours"}
    payload["timezone"] = "Asia/Kolkata"
    body = client.post("/api/chart", json=payload).json()
    assert body["birth"]["utc_offset_hours"] == 5.5
    assert "historical" not in body["birth"]["timezone_source"]
    assert "Asia/Kolkata" in body["birth"]["timezone_source"]


def test_historical_dst_is_honoured():
    """British Summer Time in July 1980 must resolve to UTC+1, not UTC+0."""
    payload = {
        **VALID, "year": 1980, "month": 7, "day": 1, "hour": 12,
        "place_name": "London, UK", "latitude": 51.5074, "longitude": -0.1278,
        "timezone": "Europe/London",
    }
    payload.pop("utc_offset_hours")
    body = client.post("/api/chart", json=payload).json()
    assert body["birth"]["utc_offset_hours"] == 1.0
    assert body["birth"]["utc_offset_label"] == "UTC+01:00"


# --- Planet analysis -------------------------------------------------------
@pytest.mark.parametrize("planet_id", list(range(9)))
def test_planet_analysis_sections(chart, planet_id):
    response = client.get(f"/api/chart/{chart['chart_id']}/planet/{planet_id}")
    assert response.status_code == 200, response.text
    a = response.json()["analysis"]

    for section in ("summary", "position", "dignity", "rashiLordRelationship",
                    "lordship", "lagnaRelationship", "nakshatraRelationship",
                    "navamshaRelationship", "avastha", "retrograde", "combustion",
                    "planetaryWar", "conjunctions", "aspectsReceived",
                    "aspectsGiven", "relationships", "shadbala",
                    "divisionalPositions", "dispositorChain", "neechaBhanga",
                    "yogaParticipation", "allYogas"):
        assert section in a, section

    assert len(a["relationships"]) == 8          # every other planet
    assert len(a["divisionalPositions"]) == 16   # D1..D60 as specified
    assert len(a["allYogas"]) == 22


def test_shadbala_present_for_seven_planets_and_absent_for_nodes(chart):
    for planet_id in range(7):
        a = client.get(f"/api/chart/{chart['chart_id']}/planet/{planet_id}").json()["analysis"]
        sb = a["shadbala"]
        assert sb["available"] is True
        assert sb["totalVirupa"] is not None
        assert sb["requiredRupa"] is not None
        assert len(sb["sthanaBala"]["components"]) == 5
        assert len(sb["kalaBala"]["components"]) == 9
    for planet_id in (7, 8):
        a = client.get(f"/api/chart/{chart['chart_id']}/planet/{planet_id}").json()["analysis"]
        assert a["shadbala"]["available"] is False
        assert a["shadbala"]["status"] == pr.NOT_AVAILABLE


def test_nodes_report_not_defined_rather_than_guessing(chart):
    for planet_id in (7, 8):
        a = client.get(f"/api/chart/{chart['chart_id']}/planet/{planet_id}").json()["analysis"]
        assert a["dignity"]["swarashi"] == pr.NOT_DEFINED
        assert a["dignity"]["mooltrikona"] == pr.NOT_DEFINED
        assert a["lordship"]["housesOwned"] == []
        assert a["planetaryWar"]["status"] == pr.NOT_APPLICABLE
        assert a["combustion"]["status"] == pr.NOT_APPLICABLE


def test_sun_combustion_is_not_applicable(chart):
    a = client.get(f"/api/chart/{chart['chart_id']}/planet/0").json()["analysis"]
    assert a["combustion"]["status"] == pr.NOT_APPLICABLE


# --- Error handling --------------------------------------------------------
def test_invalid_date_rejected():
    r = client.post("/api/chart", json={**VALID, "month": 2, "day": 30})
    assert r.status_code == 422
    assert "Invalid date" in r.json()["detail"]


def test_missing_timezone_rejected():
    payload = {k: v for k, v in VALID.items() if k != "utc_offset_hours"}
    r = client.post("/api/chart", json=payload)
    assert r.status_code == 422
    assert "timezone" in r.json()["detail"].lower()
    assert "Nothing is assumed" in r.json()["detail"]


def test_unknown_timezone_rejected():
    payload = {k: v for k, v in VALID.items() if k != "utc_offset_hours"}
    payload["timezone"] = "Mars/Olympus_Mons"
    r = client.post("/api/chart", json=payload)
    assert r.status_code == 422
    assert "Unknown timezone" in r.json()["detail"]


def test_unsupported_ayanamsha_rejected():
    r = client.post("/api/chart", json={**VALID, "ayanamsha_mode": "NOT_A_MODE"})
    assert r.status_code == 422
    assert "Unsupported ayanamsha" in r.json()["detail"]


def test_out_of_range_coordinates_rejected():
    assert client.post("/api/chart", json={**VALID, "latitude": 100.0}).status_code == 422
    assert client.post("/api/chart", json={**VALID, "longitude": 200.0}).status_code == 422


def test_blank_place_rejected():
    assert client.post("/api/chart", json={**VALID, "place_name": "   "}).status_code == 422


def test_unknown_chart_id():
    r = client.get("/api/chart/deadbeefdeadbeefdead")
    assert r.status_code == 404


def test_unknown_planet_id(chart):
    r = client.get(f"/api/chart/{chart['chart_id']}/planet/99")
    assert r.status_code == 404
    assert "Valid ids are 0 (Sun) to 8 (Ketu)" in r.json()["detail"]


def test_place_search_requires_a_query():
    assert client.get("/api/places", params={"q": "a"}).status_code == 422


# --- No interpretation anywhere -------------------------------------------
# What the application must never say.
#
# The vocabulary of the classics is NOT contraband. Words like auspicious,
# inauspicious, benefic, malefic and favourable name the categories that BPHS
# itself uses, and the findings groups are built on them deliberately. What is
# forbidden is claiming an outcome, or passing a verdict on the planet as a
# whole. These two lists draw that line.
OUTCOME_PHRASES = [
    "will bring", "will give", "will cause", "will make", "will result",
    "results in", "leads to", "brings about", "you should", "you will",
    "predicts", "prediction of", "fortunate", "unfortunate", "blessed",
    "suffer", "lucky", "misfortune", "prosperity", "wealth will",
]

VERDICT_PHRASES = [
    "is strong", "is weak", "is good", "is bad", "excellent", "poor result",
    "overall score", "overall rating", "overall verdict", "out of 10",
    "strongest planet", "weakest planet", "best planet", "worst planet",
]

FORBIDDEN_PHRASES = OUTCOME_PHRASES + VERDICT_PHRASES


# Keys whose values are structural (identifiers, categories, statuses) rather
# than prose. The findings groups are deliberately named for the classical
# categories, so those names must not be mistaken for interpretive writing.
STRUCTURAL_KEYS = {"category", "key", "status", "ruleId", "rule", "source"}


def _prose(node, key=None):
    """Every human-readable string in a response, ignoring structural fields."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _prose(v, k)
    elif isinstance(node, list):
        for v in node:
            yield from _prose(v, key)
    elif isinstance(node, str) and key not in STRUCTURAL_KEYS:
        yield node


@pytest.mark.parametrize("planet_id", list(range(9)))
def test_no_interpretation_in_any_planet_analysis(chart, planet_id):
    body = client.get(f"/api/chart/{chart['chart_id']}/planet/{planet_id}").json()
    text = " ".join(_prose(body)).lower()
    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in text, f"Interpretive phrase '{phrase}' in planet {planet_id}"


@pytest.mark.parametrize("planet_id", list(range(9)))
def test_findings_group_facts_without_predicting(chart, planet_id):
    """The three groups sort facts by classical category. They must not carry a
    verdict on the planet, a score, or a claim about what will happen."""
    findings = client.get(
        f"/api/chart/{chart['chart_id']}/planet/{planet_id}").json()["analysis"]["findings"]

    for group in ("favourable", "challenging", "neutral"):
        assert group in findings
        for item in findings[group]:
            assert item["category"] == group
            assert item["text"] and item["explanation"]
            prose = f"{item['text']} {item['explanation']}".lower()
            for phrase in FORBIDDEN_PHRASES + [
                "score", "rating", "verdict", "danger", "success",
            ]:
                assert phrase not in prose, f"'{phrase}' in {item['key']}"

    # Counts describe how many facts fall in each group; they are not a rating.
    assert findings["counts"]["favourable"] == len(findings["favourable"])
    assert findings["counts"]["challenging"] == len(findings["challenging"])
    assert findings["counts"]["neutral"] == len(findings["neutral"])
    assert "no overall judgement" in findings["note"].lower()


def test_every_planet_produces_findings(chart):
    for planet_id in range(9):
        findings = client.get(
            f"/api/chart/{chart['chart_id']}/planet/{planet_id}"
        ).json()["analysis"]["findings"]
        total = sum(findings["counts"].values())
        assert total >= 6, f"planet {planet_id} produced only {total} findings"


def test_no_interpretation_in_chart_response(chart):
    text = client.post("/api/chart", json=VALID).text.lower()
    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in text, f"Interpretive phrase '{phrase}' in chart response"


def test_shadbala_carries_no_verdict_label(chart):
    for planet_id in range(7):
        sb = client.get(
            f"/api/chart/{chart['chart_id']}/planet/{planet_id}").json()["analysis"]["shadbala"]
        text = str(sb).lower()
        for word in ("strong", "weak", "excellent", "poor", "good", "bad"):
            assert word not in text, f"Verdict word '{word}' in Shadbala"
