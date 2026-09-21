from resume_match.extraction.pipeline import extract_all
from resume_match.input_handler import load_text_from_file


def main() -> None:
    resume_text = load_text_from_file("samples/resume_sample.txt")
    jd_text = load_text_from_file("samples/job_description_sample.txt")

    result = extract_all(resume_text, jd_text)

    print("=== Resume ===")
    print(result.resume.model_dump_json(indent=2))

    print("\n=== Job Description ===")
    print(result.job_description.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
