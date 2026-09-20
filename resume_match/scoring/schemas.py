from dataclasses import dataclass, field

COVERAGE_NOTE = (
    "Percentage of explicitly listed skills, technologies, and qualifications from the "
    "job description that were also found in the resume text. This is a text-overlap "
    "measure, not an assessment of real-world job fit, experience depth, or proficiency."
)


@dataclass
class ScoreResult:
    coverage_percent: int | None
    total_required_items: int
    total_matched_items: int
    unverifiable_requirements: list[str] = field(default_factory=list)
    note: str = COVERAGE_NOTE
