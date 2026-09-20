import pytest

from evaluation.matching_cases import CASES
from resume_match.matching.matcher import match


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_matching_eval_case(case):
    result = match(case.resume, case.job_description)
    assert result == case.expected, case.description
