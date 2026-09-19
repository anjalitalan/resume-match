from dataclasses import dataclass


@dataclass
class CategoryMatch:
    matched: list[str]
    missing: list[str]


@dataclass
class MatchResult:
    skills: CategoryMatch
    technologies: CategoryMatch
    qualifications: CategoryMatch
    key_requirements: list[str]
