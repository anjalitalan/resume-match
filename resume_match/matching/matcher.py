from resume_match.extraction.schemas import ExtractedJobDescription, ExtractedResume
from resume_match.matching.schemas import CategoryMatch, MatchResult


def normalize_item(value: str) -> str:
    """Case/whitespace normalization shared by matching and scoring.

    Intentionally conservative: lowercases and collapses whitespace only.
    No stemming, punctuation stripping, or synonym mapping.
    """
    return " ".join(value.strip().lower().split())


def _compare(required: list[str], available: list[str]) -> CategoryMatch:
    available_normalized = {normalize_item(item) for item in available}

    matched = [item for item in required if normalize_item(item) in available_normalized]
    missing = [item for item in required if normalize_item(item) not in available_normalized]

    return CategoryMatch(matched=matched, missing=missing)


def match(resume: ExtractedResume, job_description: ExtractedJobDescription) -> MatchResult:
    """Deterministically compares a job description's requirements against a resume.

    Skills, technologies, and qualifications exist on both sides of the schema, so
    they are compared directly. key_requirements only exists on the job description
    side (e.g. "3+ years experience", "Bachelor's degree") with no equivalent resume
    field to compare against, so it is passed through unmatched for manual review
    rather than guessed at with naive substring matching.
    """
    return MatchResult(
        skills=_compare(job_description.skills, resume.skills),
        technologies=_compare(job_description.technologies, resume.technologies),
        qualifications=_compare(job_description.qualifications, resume.qualifications),
        key_requirements=list(job_description.key_requirements),
    )
