import streamlit as st

from dashboard.api_client import API_BASE_URL, ApiClientError, get_json

st.set_page_config(page_title="CrimeVision AI", layout="wide")

st.title("CrimeVision AI")
st.caption("Multimodal forensic analysis workspace")
st.info(
    "AI-generated outputs are investigative leads requiring human verification. "
    "They do not establish guilt or prove that a crime occurred."
)

st.markdown(
    """
Use the pages in the sidebar to:

1. Create a case and upload original evidence.
2. Run image, audio, or video analysis on stored evidence.
3. Review findings and their source timestamps in a case timeline.
4. Ask questions grounded in saved findings.
5. Generate a case PDF report.

Keep the FastAPI server running while using the dashboard.
"""
)

try:
    health = get_json("/health")
    st.success(f"API connected: {health['app']} at {API_BASE_URL}")
except ApiClientError as exc:
    st.error(str(exc))
    st.code("python -m uvicorn app.main:app --reload")
