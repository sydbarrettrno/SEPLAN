from services_knowledge_base import (
    load_checklist_base,
    load_corrected_responses,
    load_intelligent_bases,
    load_knowledge_base,
    load_normative_base,
    load_qa_base,
    search_knowledge_base,
    select_best_pattern,
)


def test_load_intelligent_bases_loads_expected_sources():
    bases = load_intelligent_bases()

    assert load_knowledge_base()
    assert load_checklist_base()
    assert load_normative_base()
    assert load_corrected_responses()
    assert load_qa_base()
    assert bases["historical"]
    assert bases["checklist"]
    assert bases["normative"]
    assert bases["corrected"]
    assert bases["qa"]


def test_matricula_question_finds_operational_checklist():
    pattern = select_best_pattern("matricula registro de imoveis")

    assert pattern is not None
    assert pattern["_source_type"] == "checklist"
    assert pattern["intent"] == "ALVARA_CONSTRUCAO"
    assert pattern["_source_checklists"]
    assert "registro de imóveis atualizado" in pattern["_source_checklists"][0]


def test_alvara_construcao_question_uses_qa_historical_or_checklist_base():
    pattern = select_best_pattern("quais documentos para alvara de construcao")

    assert pattern is not None
    assert pattern["_intent"] == "ALVARA_CONSTRUCAO"
    assert pattern["_source_type"] in {"qa", "historical", "checklist"}
    assert pattern["_response_text"]


def test_habite_se_question_uses_historical_base_with_traceability():
    pattern = select_best_pattern("quero saber como pedir habite-se")

    assert pattern is not None
    assert pattern["_source_type"] == "historical"
    assert pattern["_intent"] == "HABITE_SE"
    assert pattern["_source_protocols"]


def test_dno_agua_luz_uses_corrected_response():
    pattern = select_best_pattern("preciso de declaracao de nao oposicao para agua ou luz")

    assert pattern is not None
    assert pattern["_source_type"] == "corrected"
    assert pattern["_intent"] == "DECLARACAO_NAO_OPOSICAO"
    assert "Declaração de Não Oposição" in pattern["_response_text"]


def test_unrelated_question_has_no_safe_pattern():
    pattern = select_best_pattern("qual o melhor horario para observar estrelas")

    assert pattern is None


def test_source_protocols_are_traceability_only():
    result = search_knowledge_base("como faco o habite-se", limit=1)[0]

    assert result["_source_protocols"]
    assert result["_response_text"]
    for protocolo in result["_source_protocols"]:
        assert protocolo not in result["_response_text"]
