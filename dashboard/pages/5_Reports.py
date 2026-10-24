import streamlit as st

from dashboard.api_client import ApiClientError, case_label, list_cases, request_api

st.set_page_config(page_title="Reports | CrimeVision AI", layout="wide")
st.title("Case report")
st.write(
    "Generate a PDF containing case metadata, evidence hashes, saved findings, "
    "model provenance, and the investigative-lead disclaimer."
)

try:
    cases = list_cases()
except ApiClientError as exc:
    st.error(str(exc))
    st.stop()

if not cases:
    st.info("Create a case before generating a report.")
    st.stop()

selected_case = st.selectbox("Case", cases, format_func=case_label)
if st.button("Generate PDF report"):
    try:
        response = request_api("POST", f"/cases/{selected_case['case_id']}/report")
        st.download_button(
            "Download report",
            data=response.content,
            file_name=f"{selected_case['case_id']}_report.pdf",
            mime="application/pdf",
        )
        st.success("Report generated.")
    except ApiClientError as exc:
        st.error(str(exc))
