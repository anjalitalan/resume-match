from google.genai import types
from google.genai.errors import APIError

from resume_match.extraction.schemas import ExtractedResume, ExtractionError
from resume_match.gemini_client import DEFAULT_MODEL, get_client

RESUME_EXTRACTION_PROMPT = """You are an expert technical recruiter. Extract structured \
information from the resume below.

Rules:
- Only include information explicitly present in the resume text.
- Do not infer or invent skills, technologies, or qualifications that are not stated.
- Keep each list item concise (a single skill/technology/qualification per entry).

Resume:
{resume_text}
"""


def extract_resume(resume_text: str) -> ExtractedResume:
    client = get_client()
    prompt = RESUME_EXTRACTION_PROMPT.format(resume_text=resume_text)

    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedResume,
            ),
        )
    except APIError as e:
        raise ExtractionError(f"Gemini API call failed during resume extraction: {e}") from e

    if response.parsed is None:
        raise ExtractionError("Gemini returned no parsable structured output for resume extraction.")

    return response.parsed
