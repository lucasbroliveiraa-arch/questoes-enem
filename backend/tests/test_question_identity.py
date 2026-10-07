from app.services.question_identity import canonical_json, generate_external_id, normalize


def base(**overrides):
    data = dict(
        year=2023,
        area="Matemática",
        number=150,
        context="Contexto.",
        statement="Qual é a resposta?",
        options=["A", "B", "C", "D", "E"],
    )
    data.update(overrides)
    return data


def test_normalize_rules():
    assert normalize(None) == ""
    assert normalize("  Brasil   \r\n  ") == "Brasil"
    assert normalize("A\t\tB") == "A B"
    assert normalize("Brasil") == "Brasil"
    assert normalize("brasil") == "brasil"
    assert normalize("A?") == "A?"


def test_same_question_is_deterministic():
    assert generate_external_id(**base()) == generate_external_id(**base())


def test_formatting_differences_do_not_change_identity():
    a = base(context="  Contexto.  ", statement="Qual  é a resposta?")
    b = base(context="Contexto.", statement="Qual é a resposta?")
    assert generate_external_id(**a) == generate_external_id(**b)


def test_answer_is_not_part_of_identity():
    # correct_answer is deliberately absent from the identity API.
    assert generate_external_id(**base()) == generate_external_id(**base())


def test_option_change_changes_identity():
    changed = base(options=["A", "B", "X", "D", "E"])
    assert generate_external_id(**base()) != generate_external_id(**changed)


def test_different_questions_have_different_identity():
    changed = base(statement="Outra questão.")
    assert generate_external_id(**base()) != generate_external_id(**changed)


def test_canonical_json_is_deterministic():
    assert canonical_json({"b": "2", "a": "1"}) == '{"a":"1","b":"2"}'
