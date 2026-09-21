from resume_match.matching.matcher import normalize_item
from resume_match.matching.schemas import CategoryMatch, MatchResult
from resume_match.scoring.schemas import ScoreResult


def unique_items(items: list[str]) -> list[str]:
    """Deduplicates items by normalized value, keeping the first original-cased occurrence.

    Uses the same normalize_item semantics compute_score uses internally, so any
    caller displaying matched/missing items (e.g. the UI) can show counts that agree
    with the coverage score instead of the raw, duplicate-containing list length.
    """
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = normalize_item(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _unique_counts(category: CategoryMatch) -> tuple[int, int]:
    """Returns (unique matched count, unique required count) for one category.

    A required item that appears more than once (e.g. a duplicate skill in the job
    description) is only counted once, so repeated items cannot inflate the score.
    All occurrences of a given normalized value land in either `matched` or `missing`
    consistently (never split), since matching only depends on the value itself.
    """
    matched_normalized = {normalize_item(item) for item in category.matched}
    missing_normalized = {normalize_item(item) for item in category.missing}
    required_normalized = matched_normalized | missing_normalized
    return len(matched_normalized), len(required_normalized)


def compute_score(match_result: MatchResult) -> ScoreResult:
    """Computes deterministic requirement coverage from an existing MatchResult.

    Pools unique required/matched items across skills, technologies, and
    qualifications, since those are the categories with a comparable resume-side
    field. key_requirements has no resume-side equivalent (see matcher.match) and is
    therefore excluded from the percentage entirely and surfaced separately as
    "unverifiable" rather than being guessed at.
    """
    total_matched = 0
    total_required = 0

    for category in (match_result.skills, match_result.technologies, match_result.qualifications):
        matched_count, required_count = _unique_counts(category)
        total_matched += matched_count
        total_required += required_count

    coverage_percent = round(100 * total_matched / total_required) if total_required > 0 else None

    return ScoreResult(
        coverage_percent=coverage_percent,
        total_required_items=total_required,
        total_matched_items=total_matched,
        unverifiable_requirements=list(match_result.key_requirements),
    )
