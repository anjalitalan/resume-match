from pydantic import BaseModel, field_validator


class ExtractionError(RuntimeError):
    pass


def _strip_blank_items(values: list[str]) -> list[str]:
    """Trims whitespace and drops blank entries a model occasionally emits."""
    return [value.strip() for value in values if value and value.strip()]


class ExperienceEntry(BaseModel):
    title: str
    organization: str
    description: str


class ExtractedResume(BaseModel):
    skills: list[str]
    technologies: list[str]
    qualifications: list[str]
    experience: list[ExperienceEntry]

    @field_validator("skills", "technologies", "qualifications")
    @classmethod
    def _clean_list_fields(cls, value: list[str]) -> list[str]:
        return _strip_blank_items(value)


class ExtractedJobDescription(BaseModel):
    skills: list[str]
    technologies: list[str]
    qualifications: list[str]
    key_requirements: list[str]

    @field_validator("skills", "technologies", "qualifications", "key_requirements")
    @classmethod
    def _clean_list_fields(cls, value: list[str]) -> list[str]:
        return _strip_blank_items(value)
