"""Streamlit web interface for md2pdf."""

import tempfile
from pathlib import Path

import streamlit as st

from md2pdf.config import Config
from md2pdf.converter import MD2PDFError, MarkdownConverter
from md2pdf.styles import get_page_css
from md2pdf.themes import AVAILABLE_THEMES, get_theme_css

st.set_page_config(page_title="md2pdf", page_icon=":page_facing_up:", layout="wide")

# Session state for reset functionality
if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0

st.title("Markdown to PDF Converter")
st.markdown("Upload markdown files and convert them to professional PDFs.")

# --- Sidebar options ---
with st.sidebar:
    st.header("Conversion Options")

    theme = st.selectbox("Theme", AVAILABLE_THEMES, index=0)

    st.subheader("Page Setup")
    page_size = st.selectbox("Page size", ["A4", "Letter", "A3", "A5", "Legal"])

    st.subheader("Page Numbers")
    enable_page_numbers = st.toggle("Enable page numbers")
    page_number_position = st.selectbox(
        "Position", ["center", "left", "right"], disabled=not enable_page_numbers
    )

    toc_enabled = st.toggle("Table of Contents")
    title_page_enabled = st.toggle("Title Page")
    merge_enabled = st.toggle("Merge into single PDF")

    st.subheader("PDF Metadata")
    pdf_title = st.text_input("Title")
    pdf_author = st.text_input("Author")
    pdf_subject = st.text_input("Subject")
    pdf_keywords = st.text_input("Keywords (comma-separated)")

# --- File upload ---
uploaded_files = st.file_uploader(
    "Upload Markdown files",
    type=["md"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.upload_key}",
)

if not uploaded_files:
    st.info("Upload one or more `.md` files to get started.")
    st.stop()

# Sort by filename so numbered prefixes (01_, 02_, ...) are respected
uploaded_files = sorted(uploaded_files, key=lambda f: f.name)

# --- Preview ---
for uploaded in uploaded_files:
    content = uploaded.getvalue().decode("utf-8")
    with st.expander(f"Preview: {uploaded.name}", expanded=len(uploaded_files) == 1):
        st.markdown(content)

# --- Action buttons ---
col_convert, col_reset = st.columns([1, 1])
with col_reset:
    if st.button("Start Over"):
        st.session_state.upload_key += 1
        st.rerun()

with col_convert:
    convert_clicked = st.button("Convert to PDF", type="primary")

if convert_clicked:
    # Build config from sidebar values
    config = Config(
        page_size=page_size,
        margin_top="2cm",
        margin_bottom="2cm",
        margin_left="2cm",
        margin_right="2cm",
        font_family="Arial, sans-serif",
        font_size="11pt",
        code_font="Courier, monospace",
        default_output_dir="output",
        preserve_structure=True,
        enable_page_numbers=enable_page_numbers,
        page_number_position=page_number_position,
    )

    # Build CSS
    page_css = get_page_css(config)
    theme_css = get_theme_css(theme)
    final_css = page_css + theme_css

    converter = MarkdownConverter(config, css=final_css)

    metadata = {
        "title": pdf_title or None,
        "author": pdf_author or None,
        "subject": pdf_subject or None,
        "keywords": pdf_keywords or None,
    }

    if merge_enabled and len(uploaded_files) > 1:
        # Merge all uploads into a single PDF
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp = Path(tmpdir)
                md_paths = []
                for uploaded in uploaded_files:
                    md_path = tmp / uploaded.name
                    md_path.write_text(
                        uploaded.getvalue().decode("utf-8"), encoding="utf-8"
                    )
                    md_paths.append(md_path)

                pdf_path = tmp / "merged.pdf"
                converter.convert_merge(
                    md_paths,
                    pdf_path,
                    toc_enabled=toc_enabled,
                    metadata=metadata,
                    title_page_enabled=title_page_enabled,
                )
                pdf_bytes = pdf_path.read_bytes()

            st.success(f"Merged **{len(uploaded_files)}** files into a single PDF")
            st.download_button(
                label="Download merged.pdf",
                data=pdf_bytes,
                file_name="merged.pdf",
                mime="application/pdf",
            )
        except MD2PDFError as exc:
            st.error(f"Error merging files: {exc}")
    else:
        # Convert each file individually
        for uploaded in uploaded_files:
            md_content = uploaded.getvalue().decode("utf-8")
            pdf_name = Path(uploaded.name).stem + ".pdf"

            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmp = Path(tmpdir)
                    md_path = tmp / uploaded.name
                    pdf_path = tmp / pdf_name

                    md_path.write_text(md_content, encoding="utf-8")
                    converter.convert_file(
                        md_path,
                        pdf_path,
                        toc_enabled=toc_enabled,
                        metadata=metadata,
                        title_page_enabled=title_page_enabled,
                    )

                    pdf_bytes = pdf_path.read_bytes()

                st.success(f"Converted **{uploaded.name}**")
                st.download_button(
                    label=f"Download {pdf_name}",
                    data=pdf_bytes,
                    file_name=pdf_name,
                    mime="application/pdf",
                )
            except MD2PDFError as exc:
                st.error(f"Error converting {uploaded.name}: {exc}")
