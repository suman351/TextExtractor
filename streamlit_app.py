import os
import tempfile
import hashlib

import streamlit as st

from app import POPPLER_PATH, TESSERACT_CMD, extract_from_pdf


st.set_page_config(page_title="TextExtractor", page_icon="📄", layout="wide")

st.title("TextExtractor")
st.caption("Upload a PDF and get Hindi + English questions as text files.")

st.markdown(
    """
<style>
.big-preview textarea {
  font-size: 16px !important;
  line-height: 1.55 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

with st.expander("OCR configuration", expanded=False):
    ocr_engine = st.selectbox(
        "OCR engine",
        options=["PaddleOCR (recommended)", "Tesseract (legacy)"],
        index=0,
    )
    poppler_path = st.text_input("Poppler bin path", value=POPPLER_PATH or "")
    tesseract_cmd = st.text_input("Tesseract exe path", value=TESSERACT_CMD or "")
    dpi = st.number_input("DPI", min_value=150, max_value=600, value=300, step=50)
    skip_first_page = st.checkbox("Skip first page (instructions)", value=True)

uploaded = st.file_uploader(
    "Upload PDF",
    type=["pdf"],
    accept_multiple_files=False,
    help="Scanned UPSC-style PDF works best.",
)

run = st.button("Upload & Extract", type="primary", disabled=uploaded is None)


def _uploaded_digest(file) -> str:
    # Stable key so Streamlit reruns (e.g. download button) don't lose results.
    b = bytes(file.getbuffer())
    return hashlib.sha256(b).hexdigest()

if uploaded is not None:
    digest = _uploaded_digest(uploaded)
else:
    digest = None

if run and uploaded is not None:
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    with st.status("Processing…", expanded=True) as status:
        st.write("Saving uploaded PDF…")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir="uploads") as f:
            f.write(uploaded.getbuffer())
            pdf_path = f.name

        st.write("Running OCR + parsing… (this can take a few minutes)")
        result = extract_from_pdf(
            pdf_path,
            poppler_path=poppler_path or None,
            tesseract_cmd=tesseract_cmd or None,
            dpi=int(dpi),
            skip_first_page=skip_first_page,
            ocr_engine="paddle" if ocr_engine.startswith("Paddle") else "tesseract",
        )

        hindi_path = os.path.join("output", "hindi_questions.txt")
        english_path = os.path.join("output", "english_questions.txt")

        st.write("Writing output files…")
        with open(hindi_path, "w", encoding="utf-8") as f:
            f.write(result.hindi_txt)
        with open(english_path, "w", encoding="utf-8") as f:
            f.write(result.english_txt)

        status.update(label="Done", state="complete", expanded=False)

    st.session_state["last_digest"] = digest
    st.session_state["hindi_txt"] = result.hindi_txt
    st.session_state["english_txt"] = result.english_txt
    st.session_state["hindi_count"] = len(result.hindi_questions)
    st.session_state["english_count"] = len(result.english_questions)


# Render results if we have them for the currently uploaded PDF.
if digest and st.session_state.get("last_digest") == digest:
    hindi_txt = st.session_state.get("hindi_txt", "")
    english_txt = st.session_state.get("english_txt", "")
    hindi_count = int(st.session_state.get("hindi_count", 0))
    english_count = int(st.session_state.get("english_count", 0))

    st.success(f"Extracted {hindi_count} Hindi and {english_count} English questions.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Hindi text file")
        st.download_button(
            "Download hindi_questions.txt",
            data=hindi_txt.encode("utf-8"),
            file_name="hindi_questions.txt",
            mime="text/plain; charset=utf-8",
            use_container_width=True,
            key="download_hindi",
        )

    with col2:
        st.subheader("English text file")
        st.download_button(
            "Download english_questions.txt",
            data=english_txt.encode("utf-8"),
            file_name="english_questions.txt",
            mime="text/plain; charset=utf-8",
            use_container_width=True,
            key="download_english",
        )

    st.divider()

    tab_hi, tab_en = st.tabs(["Hindi Preview (page view)", "English Preview (page view)"])

    with tab_hi:
        st.markdown('<div class="big-preview">', unsafe_allow_html=True)
        st.text_area(
            "Hindi Preview",
            value=hindi_txt,
            height=720,
            label_visibility="collapsed",
            disabled=True,
            key="preview_hindi",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_en:
        st.markdown('<div class="big-preview">', unsafe_allow_html=True)
        st.text_area(
            "English Preview",
            value=english_txt,
            height=720,
            label_visibility="collapsed",
            disabled=True,
            key="preview_english",
        )
        st.markdown("</div>", unsafe_allow_html=True)

