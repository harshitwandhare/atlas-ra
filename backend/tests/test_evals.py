from evals.harness import Case, load_cases, score


def test_cases_load():
    cases = load_cases()
    assert len(cases) >= 3 and all(c.goal for c in cases)


def test_scoring():
    case = Case("demo", "goal", must_contain=["5B", "10GB"], must_not_contain=["14B wins"])
    assert score(case, "Use the 5B model; it fits 10GB.") == 1.0
    assert score(case, "Use the 5B model.") == 0.5
    assert score(case, "14B wins on 10GB with the 5B fallback.") == 0.0
