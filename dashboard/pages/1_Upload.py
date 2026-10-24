import streamlit as st

from dashboard.api_client import ApiClientError, case_label, list_cases, post_json, request_api

st.set_page_config(page_title="Upload | CrimeVision AI", layout="wide")
st.title("Cases and evidence")
st.caption("Uploaded originals are stored with a SHA-256 hash and linked to their case.")

try:
    cases = list_cases()
except ApiClientError as exc:
    st.error(str(exc))
    st.stop()

with st.expander("Create a case", expanded=not cases):
    with st.form("create_case"):
        title = st.text_input("Case title")
        description = st.text_area("Description (optional)")
        submitted = st.form_submit_button("Create case")
    if submitted:
        if not title.strip():
            st.error("Enter a case title.")
        else:
            try:
                case = post_json("/cases", data={"title": title, "description": description})
                st.success(f"Created {case['title']} ({case['case_id']}).")
                st.rerun()
            except ApiClientError as exc:
                st.error(str(exc))

if not cases:
    st.info("Create a case before uploading evidence.")
    st.stop()

st.subheader("Upload evidence")
selected_case = st.selectbox("Case", cases, format_func=case_label, key="upload_case")
uploaded_file = st.file_uploader(
    "Select image, audio, or video evidence",
    type=[
        "jpg", "jpeg", "png", "bmp", "webp",
        "mp3", "wav", "m4a", "flac", "ogg",
        "mp4", "avi", "mov", "mkv", "webm",
    ],
)
uploaded_by = st.text_input("Uploaded by", value="system")

if st.button("Upload evidence", disabled=uploaded_file is None):
    try:
        response = request_api(
            "POST",
            f"/cases/{selected_case['case_id']}/evidence",
            data={"uploaded_by": uploaded_by or "system"},
            files={
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type or "application/octet-stream",
                )
            },
        ).json()
        st.success(
            f"Uploaded {response['original_filename']} as {response['evidence_id']} "
            f"({response['media_type']})."
        )
        st.code(f"SHA-256: {response['sha256']}")
    except ApiClientError as exc:
        st.error(str(exc))

st.subheader("Evidence in selected case")
try:
    evidence = request_api("GET", f"/cases/{selected_case['case_id']}/evidence").json()
    if evidence:
        st.dataframe(
            [
                {
                    "File": item["original_filename"],
                    "Type": item["media_type"],
                    "Evidence ID": item["evidence_id"],
                    "SHA-256": item["sha256"],
                    "Uploaded": item["uploaded_at"],
                }
                for item in evidence
            ],
            use_container_width=True,
        )
    else:
        st.info("No evidence has been uploaded to this case.")
except ApiClientError as exc:
    st.error(str(exc))
