from unittest.mock import MagicMock, patch

import pytest
from google.genai.errors import APIError

from resume_match.extraction.job_description import extract_job_description
from resume_match.extraction.schemas import ExtractedJobDescription, ExtractionError


def _client_returning(parsed):
    client = MagicMock()
    client.models.generate_content.return_value = MagicMock(parsed=parsed)
    return client


def test_extract_job_description_returns_parsed_schema():
    expected = ExtractedJobDescription(
        skills=["Python"],
        technologies=["Gemini API"],
        qualifications=[],
        key_requirements=["2+ years experience"],
    )
    client = _client_returning(expected)

    with patch("resume_match.extraction.job_description.get_client", return_value=client):
        result = extract_job_description("some job description text")

    assert result == expected
    client.models.generate_content.assert_called_once()


def test_extract_job_description_raises_on_empty_parsed_response():
    client = _client_returning(None)

    with patch("resume_match.extraction.job_description.get_client", return_value=client):
        with pytest.raises(ExtractionError):
            extract_job_description("some job description text")


def test_extract_job_description_raises_on_api_error():
    client = MagicMock()
    client.models.generate_content.side_effect = APIError(
        500, {"error": {"message": "boom"}}, None
    )

    with patch("resume_match.extraction.job_description.get_client", return_value=client):
        with pytest.raises(ExtractionError):
            extract_job_description("some job description text")
