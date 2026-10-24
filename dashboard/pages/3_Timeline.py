import streamlit as st

from dashboard.api_client import ApiClientError, case_label, list_cases, get_json

st.set_page_config(page_title="Timeline | CrimeVision AI", layout="wide")
st.title("Case timeline")

try:
    cases = list_cases()
except ApiClientError as exc:
    st.error(str(exc))
    st.stop()

if not cases:
    st.info("Create a case before viewing its timeline.")
    st.stop()

selected_case = st.selectbox("Case", cases, format_func=case_label)
try:
    result = get_json(f"/cases/{selected_case['case_id']}/timeline")
except ApiClientError as exc:
    st.error(str(exc))
    st.stop()

st.warning(result["chronology_note"])
st.info(result["disclaimer"])

for group in result["evidence_groups"]:
    st.subheader(f"{group['original_filename']} ({group['media_type']})")
    st.caption(
        f"Evidence ID: {group['evidence_id']} | uploaded {group['uploaded_at']}"
    )
    if not group["events"]:
        st.caption("No findings have been recorded for this evidence.")
        continue
    for event in group["events"]:
        time_label = (
            f"{event['source_time_sec']:.2f}s"
            if event["source_time_sec"] is not None
            else "source time unavailable"
        )
        with st.expander(f"{time_label} | {event['finding_type']} | {event['label']}"):
            st.write(event["description"])
            st.caption(
                f"Finding ID: {event['finding_id']} | Review status: {event['status']} | "
                f"Model: {event['model_name']} ({event['model_version']})"
            )
