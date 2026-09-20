from dataclasses import dataclass

from resume_match.extraction.pipeline import ExtractionResult, extract_all
from resume_match.matching.matcher import match
from resume_match.matching.schemas import MatchResult
from resume_match.scoring.schemas import ScoreResult
from resume_match.scoring.scorer import compute_score


@dataclass
class AnalysisResult:
    extraction: ExtractionResult
    match: MatchResult
    score: ScoreResult


def analyze(resume_text: str, job_description_text: str) -> AnalysisResult:
    """Runs the full pipeline: extraction (Gemini) -> matching -> scoring (both deterministic).

    This is the single entry point the UI should call; it owns no presentation logic
    and the UI should own no business logic.
    """
    extraction = extract_all(resume_text, job_description_text)
    match_result = match(extraction.resume, extraction.job_description)
    score_result = compute_score(match_result)
    return AnalysisResult(extraction=extraction, match=match_result, score=score_result)
