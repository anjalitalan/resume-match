from resume_match.extraction.schemas import ExtractedJobDescription, ExtractedResume


def test_extracted_resume_strips_blank_and_whitespace_only_items():
    resume = ExtractedResume(
        skills=["Python", "", "   ", "SQL"],
        technologies=[" Flask "],
        qualifications=[],
        experience=[],
    )

    assert resume.skills == ["Python", "SQL"]
    assert resume.technologies == ["Flask"]


def test_extracted_job_description_strips_blank_and_whitespace_only_items():
    job = ExtractedJobDescription(
        skills=["Python", ""],
        technologies=[],
        qualifications=["  ", "Bachelor's degree"],
        key_requirements=["3+ years", ""],
    )

    assert job.skills == ["Python"]
    assert job.qualifications == ["Bachelor's degree"]
    assert job.key_requirements == ["3+ years"]
