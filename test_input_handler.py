from resume_match.input_handler import (
    InputValidationError,
    build_analysis_input,
    load_text_from_file,
)

resume_text = load_text_from_file("samples/resume_sample.txt")
jd_text = load_text_from_file("samples/job_description_sample.txt")

analysis_input = build_analysis_input(resume_text, jd_text)
print(f"Resume chars: {len(analysis_input.resume_text)}")
print(f"Job description chars: {len(analysis_input.job_description_text)}")

try:
    build_analysis_input("", jd_text)
except InputValidationError as e:
    print(f"Empty resume correctly rejected: {e}")

try:
    build_analysis_input("x" * 20_001, jd_text)
except InputValidationError as e:
    print(f"Oversized resume correctly rejected: {e}")
