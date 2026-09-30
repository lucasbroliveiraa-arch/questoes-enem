def test_list_questions_empty(client):
    resp = client.get("/api/questions")
    assert resp.status_code == 200
    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0


def test_list_questions_returns_seeded_question(client, sample_question):
    resp = client.get("/api/questions")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    item = body["items"][0]
    assert item["statement"] == "Quanto é 2 + 2?"
    # o gabarito nunca deve vazar na listagem
    assert "correct_answer" not in item


def test_filter_by_area(client, sample_question):
    resp = client.get("/api/questions", params={"area": "Linguagens"})
    assert resp.json()["total"] == 0

    resp = client.get("/api/questions", params={"area": "Matemática"})
    assert resp.json()["total"] == 1


def test_get_question_by_id(client, sample_question):
    resp = client.get(f"/api/questions/{sample_question.id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == sample_question.id


def test_get_question_not_found(client):
    resp = client.get("/api/questions/999")
    assert resp.status_code == 404
