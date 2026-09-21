from resume_match.matching.schemas import CategoryMatch, MatchResult
from resume_match.scoring.scorer import compute_score, unique_items


def test_full_coverage_is_100_percent():
    result = MatchResult(
        skills=CategoryMatch(matched=["Python"], missing=[]),
        technologies=CategoryMatch(matched=["Flask"], missing=[]),
        qualifications=CategoryMatch(matched=[], missing=[]),
        key_requirements=[],
    )

    score = compute_score(result)

    assert score.coverage_percent == 100
    assert score.total_matched_items == 2
    assert score.total_required_items == 2


def test_no_overlap_is_0_percent():
    result = MatchResult(
        skills=CategoryMatch(matched=[], missing=["Python", "SQL"]),
        technologies=CategoryMatch(matched=[], missing=[]),
        qualifications=CategoryMatch(matched=[], missing=[]),
        key_requirements=[],
    )

    score = compute_score(result)

    assert score.coverage_percent == 0
    assert score.total_matched_items == 0
    assert score.total_required_items == 2


def test_partial_overlap_is_pooled_across_categories():
    result = MatchResult(
        skills=CategoryMatch(matched=["Python"], missing=["SQL"]),
        technologies=CategoryMatch(matched=["Flask", "Docker"], missing=[]),
        qualifications=CategoryMatch(matched=[], missing=["Bachelor's degree"]),
        key_requirements=[],
    )

    score = compute_score(result)

    # matched: Python, Flask, Docker = 3; required: Python, SQL, Flask, Docker, Bachelor's = 5
    assert score.total_matched_items == 3
    assert score.total_required_items == 5
    assert score.coverage_percent == 60


def test_no_comparable_requirements_gives_none_not_zero():
    result = MatchResult(
        skills=CategoryMatch(matched=[], missing=[]),
        technologies=CategoryMatch(matched=[], missing=[]),
        qualifications=CategoryMatch(matched=[], missing=[]),
        key_requirements=["3+ years experience"],
    )

    score = compute_score(result)

    assert score.coverage_percent is None
    assert score.total_required_items == 0
    assert score.total_matched_items == 0


def test_duplicate_requirements_do_not_inflate_score():
    result = MatchResult(
        skills=CategoryMatch(matched=["Python", "Python", "SQL"], missing=["Kubernetes"]),
        technologies=CategoryMatch(matched=[], missing=[]),
        qualifications=CategoryMatch(matched=[], missing=[]),
        key_requirements=[],
    )

    score = compute_score(result)

    # Unique required: python, sql, kubernetes = 3. Unique matched: python, sql = 2.
    # A naive len()-based count would give 3/4 = 75%, not the correct 2/3 = 67%.
    assert score.total_matched_items == 2
    assert score.total_required_items == 3
    assert score.coverage_percent == 67


def test_duplicate_matched_items_with_differing_case_count_once():
    result = MatchResult(
        skills=CategoryMatch(matched=["python", "PYTHON", "Python"], missing=[]),
        technologies=CategoryMatch(matched=[], missing=[]),
        qualifications=CategoryMatch(matched=[], missing=[]),
        key_requirements=[],
    )

    score = compute_score(result)

    assert score.total_matched_items == 1
    assert score.total_required_items == 1
    assert score.coverage_percent == 100


def test_key_requirements_excluded_from_percent_but_surfaced_separately():
    result = MatchResult(
        skills=CategoryMatch(matched=["Python"], missing=[]),
        technologies=CategoryMatch(matched=[], missing=[]),
        qualifications=CategoryMatch(matched=[], missing=[]),
        key_requirements=["3+ years experience", "Bachelor's degree"],
    )

    score = compute_score(result)

    assert score.coverage_percent == 100
    assert score.unverifiable_requirements == ["3+ years experience", "Bachelor's degree"]


def test_unique_items_deduplicates_by_normalized_value_preserving_first_casing():
    assert unique_items(["Python", "python", "  PYTHON ", "SQL"]) == ["Python", "SQL"]
    assert unique_items([]) == []


def test_displayed_matched_and_missing_counts_agree_with_score_for_duplicate_requirements():
    # Regression test for the UI inconsistency found in code review: the UI must
    # display unique_items(category.matched/missing) rather than the raw
    # (duplicate-containing) lists, so its counts can never disagree with
    # compute_score()'s totals again.
    result = MatchResult(
        skills=CategoryMatch(matched=["Python", "Python"], missing=["SQL"]),
        technologies=CategoryMatch(matched=[], missing=[]),
        qualifications=CategoryMatch(matched=[], missing=[]),
        key_requirements=[],
    )

    score = compute_score(result)

    displayed_matched = unique_items(result.skills.matched)
    displayed_missing = unique_items(result.skills.missing)

    assert displayed_matched == ["Python"]
    assert displayed_missing == ["SQL"]
    assert len(displayed_matched) == score.total_matched_items
    assert len(displayed_matched) + len(displayed_missing) == score.total_required_items


def test_note_is_always_present_and_non_empty():
    result = MatchResult(
        skills=CategoryMatch(matched=[], missing=[]),
        technologies=CategoryMatch(matched=[], missing=[]),
        qualifications=CategoryMatch(matched=[], missing=[]),
        key_requirements=[],
    )

    score = compute_score(result)

    assert score.note
    assert "not" in score.note.lower()
