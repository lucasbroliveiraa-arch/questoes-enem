def test_submit_correct_answer(client, sample_question):
    resp = client.post("/api/answers", json={"question_id": sample_question.id, "selected_option": "B"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_correct"] is True
    assert body["correct_answer"] == "B"


def test_submit_wrong_answer(client, sample_question):
    resp = client.post("/api/answers", json={"question_id": sample_question.id, "selected_option": "A"})
    assert resp.status_code == 200
    assert resp.json()["is_correct"] is False


def test_submit_answer_question_not_found(client):
    resp = client.post("/api/answers", json={"question_id": 999, "selected_option": "A"})
    assert resp.status_code == 404


def test_stats_after_answers(client, sample_question):
    client.post("/api/answers", json={"question_id": sample_question.id, "selected_option": "B"})
    client.post("/api/answers", json={"question_id": sample_question.id, "selected_option": "A"})

    resp = client.get("/api/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_answered"] == 2
    assert body["total_correct"] == 1
    assert body["by_area"][0]["area"] == "Matemática"
    assert body["by_area"][0]["answered"] == 2
