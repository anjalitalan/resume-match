import streamlit as st

from resume_match.analysis import AnalysisResult, analyze
from resume_match.extraction.schemas import ExtractionError
from resume_match.input_handler import InputValidationError
from resume_match.matching.schemas import CategoryMatch
from resume_match.scoring.scorer import unique_items

SAMPLE_RESUME_PATH = "samples/resume_sample.txt"
SAMPLE_JD_PATH = "samples/job_description_sample.txt"

st.set_page_config(page_title="Resume Match", layout="wide")


def _load_uploaded_file_once(uploader_key: str, text_key: str) -> None:
    """Copies an uploaded .txt file's content into the paired text area exactly once.

    Guards against re-applying the file content on every rerun (which would silently
    overwrite anything the user typed after uploading).
    """
    uploaded_file = st.session_state.get(uploader_key)
    if uploaded_file is None:
        return

    signature = (uploaded_file.name, uploaded_file.size)
    signature_key = f"{uploader_key}_signature"
    if st.session_state.get(signature_key) == signature:
        return

    st.session_state[text_key] = uploaded_file.read().decode("utf-8", errors="replace")
    st.session_state[signature_key] = signature


def _load_sample(path: str, text_key: str) -> None:
    with open(path, encoding="utf-8") as f:
        st.session_state[text_key] = f.read()


def _render_category(title: str, category: CategoryMatch) -> None:
    # Deduplicated the same way compute_score() counts requirements, so the displayed
    # counts always agree with the coverage percentage above (see code review finding).
    matched = unique_items(category.matched)
    missing = unique_items(category.missing)

    matched_col, missing_col = st.columns(2)
    with matched_col:
        st.markdown(f"**Matched {title}** ({len(matched)})")
        for item in matched:
            st.markdown(f"- ✅ {item}")
        if not matched:
            st.caption("None")
    with missing_col:
        st.markdown(f"**Missing {title}** ({len(missing)})")
        for item in missing:
            st.markdown(f"- ❌ {item}")
        if not missing:
            st.caption("None")


def _render_result(result: AnalysisResult) -> None:
    st.divider()
    score = result.score

    st.subheader("Requirement Coverage")
    if score.coverage_percent is None:
        st.info(
            "Not enough comparable skills, technologies, or qualifications were "
            "extracted from the job description to compute a coverage percentage."
        )
    else:
        st.metric(
            "Coverage",
            f"{score.coverage_percent}%",
            help=f"{score.total_matched_items} of {score.total_required_items} required items matched.",
        )
        st.progress(score.coverage_percent / 100)
    st.caption(score.note)

    if score.unverifiable_requirements:
        st.subheader("Requirements That Can't Be Automatically Verified")
        st.caption(
            "These are not reflected in the coverage percentage above (e.g. years of "
            "experience, degree requirements) — review them manually."
        )
        for item in score.unverifiable_requirements:
            st.markdown(f"- {item}")

    st.subheader("Skill & Technology Comparison")
    _render_category("Skills", result.match.skills)
    _render_category("Technologies", result.match.technologies)
    _render_category("Qualifications", result.match.qualifications)

    with st.expander("Extracted resume details"):
        st.json(result.extraction.resume.model_dump())
    with st.expander("Extracted job description details"):
        st.json(result.extraction.job_description.model_dump())


st.title("Resume Match")
st.caption(
    "Extracts structured information from a resume and job description with Gemini, "
    "then compares them with deterministic, explainable logic — Gemini never decides "
    "the score."
)
with st.expander("How is the coverage percentage calculated?"):
    st.write(
        "Coverage counts how many of the job description's listed skills, technologies, "
        "and qualifications also appear (case-insensitively, ignoring extra whitespace) "
        "in the resume text. It is a text-overlap measure only — it does not evaluate "
        "experience depth, proficiency, or overall job fit, and items like required years "
        "of experience or degree requirements are listed separately because they can't be "
        "verified this way."
    )

resume_col, jd_col = st.columns(2)

with resume_col:
    st.subheader("Resume")
    st.file_uploader("Upload a .txt resume (optional)", type=["txt"], key="resume_file")
    _load_uploaded_file_once("resume_file", "resume_text")
    st.button("Use sample resume", key="load_sample_resume", on_click=_load_sample, args=(SAMPLE_RESUME_PATH, "resume_text"))
    resume_text = st.text_area("Resume text", height=300, key="resume_text")

with jd_col:
    st.subheader("Job Description")
    st.file_uploader("Upload a .txt job description (optional)", type=["txt"], key="jd_file")
    _load_uploaded_file_once("jd_file", "jd_text")
    st.button("Use sample job description", key="load_sample_jd", on_click=_load_sample, args=(SAMPLE_JD_PATH, "jd_text"))
    jd_text = st.text_area("Job description text", height=300, key="jd_text")

if st.button("Analyze", type="primary"):
    try:
        with st.spinner("Extracting and comparing..."):
            st.session_state["analysis_result"] = analyze(resume_text, jd_text)
    except InputValidationError as e:
        st.session_state.pop("analysis_result", None)
        st.error(str(e))
    except ExtractionError as e:
        st.session_state.pop("analysis_result", None)
        st.error(f"Extraction failed: {e}")

if "analysis_result" in st.session_state:
    _render_result(st.session_state["analysis_result"])
