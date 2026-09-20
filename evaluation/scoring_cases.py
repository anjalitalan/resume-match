from dataclasses import dataclass

from resume_match.matching.schemas import CategoryMatch, MatchResult
from resume_match.scoring.schemas import ScoreResult
from resume_match.scoring.scorer import compute_score


@dataclass
class ScoringEvalCase:
    name: str
    description: str
    match_result: MatchResult
    expected: ScoreResult


CASES: list[ScoringEvalCase] = [
    ScoringEvalCase(
        name="strong_overlap",
        description="Every required skill/technology is present in the resume.",
        match_result=MatchResult(
            skills=CategoryMatch(matched=["Python", "SQL"], missing=[]),
            technologies=CategoryMatch(matched=["Flask"], missing=[]),
            qualifications=CategoryMatch(matched=[], missing=[]),
            key_requirements=[],
        ),
        expected=ScoreResult(
            coverage_percent=100,
            total_required_items=3,
            total_matched_items=3,
            unverifiable_requirements=[],
        ),
    ),
    ScoringEvalCase(
        name="partial_overlap",
        description="Resume covers some but not all required skills/technologies.",
        match_result=MatchResult(
            skills=CategoryMatch(matched=["Python"], missing=["Kubernetes"]),
            technologies=CategoryMatch(matched=["Flask"], missing=["Docker"]),
            qualifications=CategoryMatch(matched=[], missing=[]),
            key_requirements=[],
        ),
        expected=ScoreResult(
            coverage_percent=50,
            total_required_items=4,
            total_matched_items=2,
            unverifiable_requirements=[],
        ),
    ),
    ScoringEvalCase(
        name="no_overlap",
        description="None of the required skills/technologies are present in the resume.",
        match_result=MatchResult(
            skills=CategoryMatch(matched=[], missing=["Python", "SQL"]),
            technologies=CategoryMatch(matched=[], missing=["Docker"]),
            qualifications=CategoryMatch(matched=[], missing=[]),
            key_requirements=[],
        ),
        expected=ScoreResult(
            coverage_percent=0,
            total_required_items=3,
            total_matched_items=0,
            unverifiable_requirements=[],
        ),
    ),
    ScoringEvalCase(
        name="missing_requirements_only",
        description="Resume has no overlap in qualifications specifically.",
        match_result=MatchResult(
            skills=CategoryMatch(matched=["Python"], missing=[]),
            technologies=CategoryMatch(matched=[], missing=[]),
            qualifications=CategoryMatch(matched=[], missing=["Master's degree"]),
            key_requirements=[],
        ),
        expected=ScoreResult(
            coverage_percent=50,
            total_required_items=2,
            total_matched_items=1,
            unverifiable_requirements=[],
        ),
    ),
    ScoringEvalCase(
        name="duplicate_requirements_do_not_inflate",
        description="A skill repeated in the job description is only counted once.",
        match_result=MatchResult(
            skills=CategoryMatch(matched=["Python", "Python"], missing=["SQL"]),
            technologies=CategoryMatch(matched=[], missing=[]),
            qualifications=CategoryMatch(matched=[], missing=[]),
            key_requirements=[],
        ),
        expected=ScoreResult(
            coverage_percent=50,
            total_required_items=2,
            total_matched_items=1,
            unverifiable_requirements=[],
        ),
    ),
    ScoringEvalCase(
        name="empty_inputs_give_none_not_zero",
        description="No comparable requirements at all; score must be None, not misleadingly 0.",
        match_result=MatchResult(
            skills=CategoryMatch(matched=[], missing=[]),
            technologies=CategoryMatch(matched=[], missing=[]),
            qualifications=CategoryMatch(matched=[], missing=[]),
            key_requirements=[],
        ),
        expected=ScoreResult(
            coverage_percent=None,
            total_required_items=0,
            total_matched_items=0,
            unverifiable_requirements=[],
        ),
    ),
    ScoringEvalCase(
        name="unverifiable_requirements_reported_separately",
        description="key_requirements never affects the percentage, only the separate list.",
        match_result=MatchResult(
            skills=CategoryMatch(matched=["Python"], missing=[]),
            technologies=CategoryMatch(matched=[], missing=[]),
            qualifications=CategoryMatch(matched=[], missing=[]),
            key_requirements=["3+ years experience", "Bachelor's degree"],
        ),
        expected=ScoreResult(
            coverage_percent=100,
            total_required_items=1,
            total_matched_items=1,
            unverifiable_requirements=["3+ years experience", "Bachelor's degree"],
        ),
    ),
    ScoringEvalCase(
        name="mixed_categories",
        description="Skills, technologies, and qualifications each contribute a different ratio.",
        match_result=MatchResult(
            skills=CategoryMatch(matched=["Python"], missing=["SQL"]),
            technologies=CategoryMatch(matched=["Flask", "Docker"], missing=[]),
            qualifications=CategoryMatch(matched=[], missing=["Bachelor's degree"]),
            key_requirements=[],
        ),
        expected=ScoreResult(
            coverage_percent=60,
            total_required_items=5,
            total_matched_items=3,
            unverifiable_requirements=[],
        ),
    ),
]
