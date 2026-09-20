from unittest.mock import MagicMock, patch

import httpx
import pytest
from google.genai.errors import APIError

from resume_match.extraction.resume import extract_resume
from resume_match.extraction.schemas import ExtractedResume, ExtractionError
from resume_match.input_handler import InputValidationError


def _client_returning(parsed):
    client = MagicMock()
    client.models.generate_content.return_value = MagicMock(parsed=parsed)
    return client


def test_extract_resume_returns_parsed_schema():
    expected = ExtractedResume(
        skills=["Python"],
        technologies=["Flask", "PostgreSQL"],
        qualifications=["B.Tech in Computer Science"],
        experience=[],
    )
    client = _client_returning(expected)

    with patch("resume_match.extraction.resume.get_client", return_value=client):
        result = extract_resume("some resume text")

    assert result == expected
    client.models.generate_content.assert_called_once()


def test_extract_resume_raises_on_empty_parsed_response():
    client = _client_returning(None)

    with patch("resume_match.extraction.resume.get_client", return_value=client):
        with pytest.raises(ExtractionError):
            extract_resume("some resume text")


def test_extract_resume_raises_on_api_error():
    client = MagicMock()
    client.models.generate_content.side_effect = APIError(
        500, {"error": {"message": "boom"}}, None
    )

    with patch("resume_match.extraction.resume.get_client", return_value=client):
        with pytest.raises(ExtractionError):
            extract_resume("some resume text")


def test_extract_resume_raises_on_network_timeout():
    client = MagicMock()
    client.models.generate_content.side_effect = httpx.TimeoutException("timed out")

    with patch("resume_match.extraction.resume.get_client", return_value=client):
        with pytest.raises(ExtractionError):
            extract_resume("some resume text")


def test_extract_resume_rejects_empty_input_without_calling_api():
    client = MagicMock()

    with patch("resume_match.extraction.resume.get_client", return_value=client):
        with pytest.raises(InputValidationError):
            extract_resume("   ")

    client.models.generate_content.assert_not_called()
