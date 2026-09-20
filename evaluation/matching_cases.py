from dataclasses import dataclass

from resume_match.extraction.schemas import ExtractedJobDescription, ExtractedResume
from resume_match.matching.schemas import CategoryMatch, MatchResult


@dataclass
class MatchingEvalCase:
    name: str
    description: str
    resume: ExtractedResume
    job_description: ExtractedJobDescription
    expected: MatchResult


def _resume(skills=None, technologies=None, qualifications=None) -> ExtractedResume:
    return ExtractedResume(
        skills=skills or [],
        technologies=technologies or [],
        qualifications=qualifications or [],
        experience=[],
    )


def _job(skills=None, technologies=None, qualifications=None, key_requirements=None) -> ExtractedJobDescription:
    return ExtractedJobDescription(
        skills=skills or [],
        technologies=technologies or [],
        qualifications=qualifications or [],
        key_requirements=key_requirements or [],
    )


CASES: list[MatchingEvalCase] = [
    MatchingEvalCase(
        name="strong_match",
        description="Resume covers every JD skill/technology/qualification exactly.",
        resume=_resume(
            skills=["Machine Learning"],
            technologies=["Python", "Flask"],
            qualifications=["B.Tech in Computer Science"],
        ),
        job_description=_job(
            skills=["Machine Learning"],
            technologies=["Python", "Flask"],
            qualifications=["B.Tech in Computer Science"],
        ),
        expected=MatchResult(
            skills=CategoryMatch(matched=["Machine Learning"], missing=[]),
            technologies=CategoryMatch(matched=["Python", "Flask"], missing=[]),
            qualifications=CategoryMatch(matched=["B.Tech in Computer Science"], missing=[]),
            key_requirements=[],
        ),
    ),
    MatchingEvalCase(
        name="missing_requirements",
        description="Resume only partially covers the JD's required skills/technologies.",
        resume=_resume(skills=["Python"], technologies=["Flask"]),
        job_description=_job(
            skills=["Python", "Kubernetes"],
            technologies=["Flask", "Docker"],
        ),
        expected=MatchResult(
            skills=CategoryMatch(matched=["Python"], missing=["Kubernetes"]),
            technologies=CategoryMatch(matched=["Flask"], missing=["Docker"]),
            qualifications=CategoryMatch(matched=[], missing=[]),
            key_requirements=[],
        ),
    ),
    MatchingEvalCase(
        name="empty_resume_fields",
        description="Resume has nothing extracted; every JD requirement is missing.",
        resume=_resume(),
        job_description=_job(skills=["Python", "SQL"], technologies=["Docker"]),
        expected=MatchResult(
            skills=CategoryMatch(matched=[], missing=["Python", "SQL"]),
            technologies=CategoryMatch(matched=[], missing=["Docker"]),
            qualifications=CategoryMatch(matched=[], missing=[]),
            key_requirements=[],
        ),
    ),
    MatchingEvalCase(
        name="empty_job_description_fields",
        description="JD has nothing extracted; there is nothing to match or miss.",
        resume=_resume(skills=["Python"], technologies=["Flask"]),
        job_description=_job(),
        expected=MatchResult(
            skills=CategoryMatch(matched=[], missing=[]),
            technologies=CategoryMatch(matched=[], missing=[]),
            qualifications=CategoryMatch(matched=[], missing=[]),
            key_requirements=[],
        ),
    ),
    MatchingEvalCase(
        name="casing_and_whitespace_variation",
        description="Resume text differs from JD only in case and whitespace.",
        resume=_resume(skills=["  machine   learning "], technologies=["python", "FLASK"]),
        job_description=_job(skills=["Machine Learning"], technologies=["Python", "Flask"]),
        expected=MatchResult(
            skills=CategoryMatch(matched=["Machine Learning"], missing=[]),
            technologies=CategoryMatch(matched=["Python", "Flask"], missing=[]),
            qualifications=CategoryMatch(matched=[], missing=[]),
            key_requirements=[],
        ),
    ),
    MatchingEvalCase(
        name="category_mismatch_not_cross_matched",
        description=(
            "'Flask' appears under the resume's skills but the JD's technologies. "
            "Documents the current, deliberately simple category-to-category matching: "
            "this does NOT count as a match."
        ),
        resume=_resume(skills=["Flask"]),
        job_description=_job(technologies=["Flask"]),
        expected=MatchResult(
            skills=CategoryMatch(matched=[], missing=[]),
            technologies=CategoryMatch(matched=[], missing=["Flask"]),
            qualifications=CategoryMatch(matched=[], missing=[]),
            key_requirements=[],
        ),
    ),
    MatchingEvalCase(
        name="key_requirements_pass_through_unmatched",
        description="key_requirements has no resume-side field to compare against, so it always passes through as-is.",
        resume=_resume(skills=["Python"], technologies=["Flask"], qualifications=["B.Tech"]),
        job_description=_job(
            skills=["Python"],
            key_requirements=["3+ years experience", "Bachelor's degree"],
        ),
        expected=MatchResult(
            skills=CategoryMatch(matched=["Python"], missing=[]),
            technologies=CategoryMatch(matched=[], missing=[]),
            qualifications=CategoryMatch(matched=[], missing=[]),
            key_requirements=["3+ years experience", "Bachelor's degree"],
        ),
    ),
    MatchingEvalCase(
        name="duplicate_required_items_handled_independently",
        description="A JD skill listed twice is not deduplicated; each occurrence is matched independently.",
        resume=_resume(skills=["Python"]),
        job_description=_job(skills=["Python", "Python", "SQL"]),
        expected=MatchResult(
            skills=CategoryMatch(matched=["Python", "Python"], missing=["SQL"]),
            technologies=CategoryMatch(matched=[], missing=[]),
            qualifications=CategoryMatch(matched=[], missing=[]),
            key_requirements=[],
        ),
    ),
]
