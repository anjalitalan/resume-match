from resume_match.extraction.schemas import ExtractedJobDescription, ExtractedResume
from resume_match.matching.matcher import match


def _resume(skills=None, technologies=None, qualifications=None):
    return ExtractedResume(
        skills=skills or [],
        technologies=technologies or [],
        qualifications=qualifications or [],
        experience=[],
    )


def _job(skills=None, technologies=None, qualifications=None, key_requirements=None):
    return ExtractedJobDescription(
        skills=skills or [],
        technologies=technologies or [],
        qualifications=qualifications or [],
        key_requirements=key_requirements or [],
    )


def test_exact_match():
    resume = _resume(skills=["Machine Learning"])
    job = _job(skills=["Machine Learning"])

    result = match(resume, job)

    assert result.skills.matched == ["Machine Learning"]
    assert result.skills.missing == []


def test_case_insensitive_match():
    resume = _resume(technologies=["python"])
    job = _job(technologies=["Python"])

    result = match(resume, job)

    assert result.technologies.matched == ["Python"]
    assert result.technologies.missing == []


def test_whitespace_normalization():
    resume = _resume(skills=["  Machine   Learning "])
    job = _job(skills=["Machine Learning"])

    result = match(resume, job)

    assert result.skills.matched == ["Machine Learning"]


def test_missing_skill():
    resume = _resume(skills=["Python"])
    job = _job(skills=["Python", "Kubernetes"])

    result = match(resume, job)

    assert result.skills.matched == ["Python"]
    assert result.skills.missing == ["Kubernetes"]


def test_empty_required_list_produces_no_matches_or_misses():
    resume = _resume(skills=["Python"])
    job = _job(skills=[])

    result = match(resume, job)

    assert result.skills.matched == []
    assert result.skills.missing == []


def test_empty_available_list_makes_everything_missing():
    resume = _resume(skills=[])
    job = _job(skills=["Python", "SQL"])

    result = match(resume, job)

    assert result.skills.matched == []
    assert result.skills.missing == ["Python", "SQL"]


def test_qualifications_are_compared_the_same_way_as_skills():
    resume = _resume(qualifications=["B.Tech in Computer Science"])
    job = _job(qualifications=["b.tech in computer science", "MBA"])

    result = match(resume, job)

    assert result.qualifications.matched == ["b.tech in computer science"]
    assert result.qualifications.missing == ["MBA"]


def test_key_requirements_pass_through_unmatched():
    resume = _resume()
    job = _job(key_requirements=["3+ years experience", "Bachelor's degree"])

    result = match(resume, job)

    assert result.key_requirements == ["3+ years experience", "Bachelor's degree"]


def test_technologies_in_wrong_category_are_not_cross_matched():
    # Documents the current, deliberately simple behavior: matching is
    # category-to-category (skills vs skills, technologies vs technologies),
    # not merged across categories.
    resume = _resume(skills=["Flask"])
    job = _job(technologies=["Flask"])

    result = match(resume, job)

    assert result.technologies.matched == []
    assert result.technologies.missing == ["Flask"]
