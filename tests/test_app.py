"""Smoke tests for PhiloCompass — run against a live server OR via TestClient."""

import pytest
from fastapi.testclient import TestClient

from philo_app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "llm" in body


def test_domains(client):
    r = client.get("/api/domains")
    assert r.status_code == 200
    assert "domains" in r.json()


def test_map(client):
    r = client.get("/api/map")
    assert r.status_code == 200
    body = r.json()
    assert "nodes" in body and "edges" in body
    assert len(body["nodes"]) >= 15
    # every edge references valid nodes
    ids = set(body["nodes"].keys())
    for e in body["edges"]:
        assert e["from"] in ids and e["to"] in ids


def test_thinker_lookup(client):
    r = client.get("/api/thinker/kant")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Kant"
    assert "influenced_by" in body and "influences" in body


def test_thinker_unknown(client):
    r = client.get("/api/thinker/doesnotexist")
    assert r.status_code == 200
    assert "error" in r.json()


def test_session_start_and_flow(client):
    r = client.post("/api/session/start", json={"domain": "ethics"})
    assert r.status_code == 200
    data = r.json()
    assert "session_id" in data
    assert "question" in data
    sid = data["session_id"]

    r2 = client.post("/api/session/answer", json={"session_id": sid, "answer": "I think morality is about consequences."})
    assert r2.status_code == 200
    a = r2.json()
    assert "follow_up" in a and len(a["follow_up"]) > 0
    assert a["turns"] == 1


def test_custom_question_dialogue_a(client):
    r = client.post("/api/session/start", json={"domain": "custom", "custom_question": "Is a hot dog a sandwich?"})
    assert r.status_code == 200
    assert "Is a hot dog a sandwich?" in r.json()["question"]


def test_node_seeded_dialogue(client):
    r = client.post("/api/session/start", json={"node_id": "kant"})
    assert r.status_code == 200
    d = r.json()
    assert "session_id" in d
    assert "Kant" in d["question"]
    assert d["domain"] == "ethics"

    r2 = client.post("/api/session/answer", json={"session_id": d["session_id"], "answer": "The categorical imperative demands acting on universal maxims."})
    assert r2.status_code == 200
    assert len(r2.json()["follow_up"]) > 0


def test_node_seeded_unknown(client):
    r = client.post("/api/session/start", json={"node_id": "nope"})
    assert r.status_code == 200
    assert "error" in r.json()


def test_index_served(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "PhiloCompass" in r.text


def test_debate_start_random(client):
    r = client.post("/api/session/start", json={"mode": "debate"})
    assert r.status_code == 200
    d = r.json()
    assert d["mode"] == "debate"
    assert "session_id" in d
    assert "side_a" in d and "side_b" in d
    assert "opening" in d and d["opening"]["text"]


def test_debate_flow(client):
    r = client.post("/api/session/start", json={"mode": "debate", "node_id": "kant", "pair_with": "utilitarianism"})
    d = r.json()
    sid = d["session_id"]
    # two exchanges
    r1 = client.post("/api/session/answer", json={"session_id": sid, "answer": "I side with Kant's dignity of persons.", "mode": "debate"})
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["mode"] == "debate"
    assert "turn" in d1
    # keep going until conclusion fires
    for _ in range(4):
        rn = client.post("/api/session/answer", json={"session_id": sid, "answer": "Let me weigh that more.", "mode": "debate"})
        if rn.json().get("conclusion"):
            assert "moved you" in rn.json()["conclusion"]
            break
    else:
        assert False, "debate never reached a conclusion"


def test_custom_question_dialogue_b(client):
    r = client.post("/api/session/start", json={"custom_question": "Is a thermostat conscious?"})
    assert r.status_code == 200
    assert "thermostat" in r.json()["question"]
    assert r.json()["domain"] == "custom"


def test_reword_question(client):
    r = client.post("/api/session/start", json={"domain": "ethics"})
    sid = r.json()["session_id"]
    r2 = client.post("/api/session/answer", json={"session_id": sid, "reword": True})
    assert r2.status_code == 200
    d = r2.json()
    assert d.get("reworded")
    assert "justice" in d["question"].lower() or len(d["question"]) > 10


def test_cognitive_state_tracking(client):
    r = client.post("/api/session/start", json={"domain": "ethics"})
    sid = r.json()["session_id"]
    r1 = client.post("/api/session/answer", json={"session_id": sid, "answer": "I think happiness is what matters most."})
    d1 = r1.json()
    assert "move" in d1 and d1["move"] in ("claimed", "reasons")
    assert "momentum" in d1
    assert d1["pedagogy"]["rationale"]


def test_debate_custom(client):
    r = client.post("/api/session/start", json={
        "mode": "debate",
        "node_id": "nietzsche",
        "pair_with": "hume",
        "custom_question": "Is the self a fiction, or the creator of all value?",
    })
    assert r.status_code == 200
    d = r.json()
    assert d["mode"] == "debate"
    assert "self" in d["question"].lower()
    assert d["side_a"] and d["side_b"]


def test_teach_me(client):
    r = client.post("/api/session/start", json={"domain": "ethics"})
    sid = r.json()["session_id"]
    r2 = client.post("/api/session/answer", json={"session_id": sid, "teach_me": True})
    assert r2.status_code == 200
    d = r2.json()
    assert d.get("taught")
    assert "what we're really asking" in d["lesson"].lower() or len(d["lesson"]) > 80


def test_custom_debate_teach(client):
    r = client.post("/api/session/start", json={
        "mode": "debate", "node_id": "plato", "pair_with": "aristotle",
        "custom_question": "Is virtue knowledge?",
    })
    sid = r.json()["session_id"]
    r2 = client.post("/api/session/answer", json={"session_id": sid, "teach_me": True})
    assert r2.status_code == 200
    assert r2.json().get("taught")
