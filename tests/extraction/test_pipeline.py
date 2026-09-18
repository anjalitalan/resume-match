from unittest.mock import patch

from resume_match.extraction.pipeline import extract_all
from resume_match.extraction.schemas import ExtractedJobDescription, ExtractedResume


def test_extract_all_validates_input_and_combines_results():
    fake_resume = ExtractedResume(skills=[], technologies=[], qualifications=[], experience=[])
    fake_jd = ExtractedJobDescription(
        skills=[], technologies=[], qualifications=[], key_requirements=[]
    )

    with (
        patch("resume_match.extraction.pipeline.extract_resume", return_value=fake_resume) as mock_resume,
        patch("resume_match.extraction.pipeline.extract_job_description", return_value=fake_jd) as mock_jd,
    ):
        result = extract_all("  resume text  ", "  jd text  ")

    mock_resume.assert_called_once_with("resume text")
    mock_jd.assert_called_once_with("jd text")
    assert result.resume == fake_resume
    assert result.job_description == fake_jd
