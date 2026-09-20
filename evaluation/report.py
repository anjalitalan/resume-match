"""Small standalone summary of the deterministic matcher/scorer evaluation cases.

Not a substitute for pytest — it exists to give a human-readable pass/fail summary
without needing to parse test output. Run directly:

    ./venv/Scripts/python.exe -m evaluation.report
"""

from dataclasses import dataclass

from evaluation.matching_cases import CASES as MATCHING_CASES
from evaluation.scoring_cases import CASES as SCORING_CASES
from resume_match.matching.matcher import match
from resume_match.scoring.scorer import compute_score


@dataclass
class CaseOutcome:
    name: str
    passed: bool
    description: str


def evaluate_matching_cases() -> list[CaseOutcome]:
    outcomes = []
    for case in MATCHING_CASES:
        actual = match(case.resume, case.job_description)
        outcomes.append(CaseOutcome(case.name, actual == case.expected, case.description))
    return outcomes


def evaluate_scoring_cases() -> list[CaseOutcome]:
    outcomes = []
    for case in SCORING_CASES:
        actual = compute_score(case.match_result)
        outcomes.append(CaseOutcome(case.name, actual == case.expected, case.description))
    return outcomes


def _print_section(title: str, outcomes: list[CaseOutcome]) -> None:
    passed = sum(1 for o in outcomes if o.passed)
    print(f"\n{title}: {passed}/{len(outcomes)} passed")
    for outcome in outcomes:
        status = "PASS" if outcome.passed else "FAIL"
        print(f"  [{status}] {outcome.name} - {outcome.description}")


def main() -> None:
    matching_outcomes = evaluate_matching_cases()
    scoring_outcomes = evaluate_scoring_cases()

    _print_section("Matching cases", matching_outcomes)
    _print_section("Scoring cases", scoring_outcomes)

    total = len(matching_outcomes) + len(scoring_outcomes)
    total_passed = sum(o.passed for o in matching_outcomes + scoring_outcomes)
    print(f"\nTotal: {total_passed}/{total} evaluation cases passed")


if __name__ == "__main__":
    main()
