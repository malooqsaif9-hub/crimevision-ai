
import sys
from pathlib import Path

import streamlit as st

# Add the project root to Python's import path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import the API client functions and variables
from dashboard.api_client import (
    API_BASE_URL,
    ApiClientError,
    get_json,
)

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
    st.caption("Make sure the FastAPI backend is running and reachable.")

