import httpx
from google.genai import types
from google.genai.errors import APIError

from resume_match.extraction.schemas import ExtractedJobDescription, ExtractionError
from resume_match.gemini_client import DEFAULT_MODEL, call_with_retry, get_client
from resume_match.input_handler import clean_text

JOB_DESCRIPTION_EXTRACTION_PROMPT = """You are an expert technical recruiter. Extract \
structured information from the job description below.

Rules:
- Only include information explicitly present in the job description text.
- Do not infer or invent skills, technologies, or requirements that are not stated.
- Keep each list item concise (a single skill/technology/requirement per entry).
- "key_requirements" should capture must-have requirements stated in the posting \
(e.g. years of experience, degree requirements, certifications), not skills already \
captured in the skills/technologies lists.
- If a category has no relevant information in the posting, return an empty list for it.
  Do not fabricate a placeholder value.

Job description:
{job_description_text}
"""


def extract_job_description(job_description_text: str) -> ExtractedJobDescription:
    cleaned_text = clean_text(job_description_text, "Job description")
    client = get_client()
    prompt = JOB_DESCRIPTION_EXTRACTION_PROMPT.format(job_description_text=cleaned_text)

    try:
        response = call_with_retry(
            lambda: client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractedJobDescription,
                ),
            )
        )
    except (APIError, httpx.TimeoutException, httpx.ConnectError) as e:
        raise ExtractionError(
            f"Gemini API call failed during job description extraction: {e}"
        ) from e

    if response.parsed is None:
        raise ExtractionError(
            "Gemini returned no parsable structured output for job description extraction."
        )

    return response.parsed
