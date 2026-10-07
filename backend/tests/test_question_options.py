from app.models.question_option import QuestionOption


def test_question_returns_five_options(client, sample_question):
    response = client.get(f"/api/questions/{sample_question.id}")
    assert response.status_code == 200
    body = response.json()
    assert [option["letter"] for option in body["options"]] == ["A", "B", "C", "D", "E"]
    assert [option["text"] for option in body["options"]] == ["3", "4", "5", "6", "7"]


def test_option_explanation_is_exposed(client, sample_question, db_session):
    sample_question.options[1].explanation = "Porque 2 + 2 = 4."
    db_session.commit()

    body = client.get(f"/api/questions/{sample_question.id}").json()
    assert body["options"][1]["explanation"] == "Porque 2 + 2 = 4."
