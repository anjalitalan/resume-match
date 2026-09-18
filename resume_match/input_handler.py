from dataclasses import dataclass
from pathlib import Path

MAX_INPUT_CHARS = 20_000


class InputValidationError(ValueError):
    pass


@dataclass
class AnalysisInput:
    resume_text: str
    job_description_text: str


def load_text_from_file(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return file_path.read_text(encoding="utf-8")


def _clean_text(text: str, label: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise InputValidationError(f"{label} is empty.")
    if len(cleaned) > MAX_INPUT_CHARS:
        raise InputValidationError(
            f"{label} exceeds the {MAX_INPUT_CHARS} character limit "
            f"(got {len(cleaned)})."
        )
    return cleaned


def build_analysis_input(resume_text: str, job_description_text: str) -> AnalysisInput:
    return AnalysisInput(
        resume_text=_clean_text(resume_text, "Resume"),
        job_description_text=_clean_text(job_description_text, "Job description"),
    )
