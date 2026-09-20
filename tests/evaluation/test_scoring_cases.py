import pytest

from evaluation.scoring_cases import CASES
from resume_match.scoring.scorer import compute_score


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_scoring_eval_case(case):
    result = compute_score(case.match_result)
    assert result == case.expected, case.description
