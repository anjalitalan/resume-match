from pydantic import BaseModel


class ExtractionError(RuntimeError):
    pass


class ExperienceEntry(BaseModel):
    title: str
    organization: str
    description: str


class ExtractedResume(BaseModel):
    skills: list[str]
    technologies: list[str]
    qualifications: list[str]
    experience: list[ExperienceEntry]


class ExtractedJobDescription(BaseModel):
    skills: list[str]
    technologies: list[str]
    qualifications: list[str]
    key_requirements: list[str]
