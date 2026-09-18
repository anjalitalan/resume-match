from dataclasses import dataclass

from resume_match.extraction.job_description import extract_job_description
from resume_match.extraction.resume import extract_resume
from resume_match.extraction.schemas import ExtractedJobDescription, ExtractedResume
from resume_match.input_handler import build_analysis_input


@dataclass
class ExtractionResult:
    resume: ExtractedResume
    job_description: ExtractedJobDescription


def extract_all(resume_text: str, job_description_text: str) -> ExtractionResult:
    analysis_input = build_analysis_input(resume_text, job_description_text)
    return ExtractionResult(
        resume=extract_resume(analysis_input.resume_text),
        job_description=extract_job_description(analysis_input.job_description_text),
    )
