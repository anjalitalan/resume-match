from unittest.mock import patch

from resume_match.analysis import analyze
from resume_match.extraction.schemas import ExtractedJobDescription, ExtractedResume


def test_analyze_runs_full_pipeline_and_combines_results():
    fake_resume = ExtractedResume(
        skills=["Python"], technologies=["Flask"], qualifications=[], experience=[]
    )
    fake_jd = ExtractedJobDescription(
        skills=["Python"], technologies=["Flask"], qualifications=[], key_requirements=[]
    )

    with (
        patch("resume_match.analysis.extract_all") as mock_extract_all,
    ):
        from resume_match.extraction.pipeline import ExtractionResult

        mock_extract_all.return_value = ExtractionResult(resume=fake_resume, job_description=fake_jd)

        result = analyze("resume text", "jd text")

    mock_extract_all.assert_called_once_with("resume text", "jd text")
    assert result.extraction.resume == fake_resume
    assert result.extraction.job_description == fake_jd
    assert result.match.skills.matched == ["Python"]
    assert result.match.technologies.matched == ["Flask"]
    assert result.score.coverage_percent == 100
