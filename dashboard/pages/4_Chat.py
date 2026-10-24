import streamlit as st

from dashboard.api_client import ApiClientError, case_label, list_cases, post_json

st.set_page_config(page_title="Case chat | CrimeVision AI", layout="wide")
st.title("Ask about case findings")
st.caption(
    "Answers are generated only from matching saved findings. This starter retrieval is lexical, "
    "not a general-purpose legal or investigative conclusion."
)

try:
    cases = list_cases()
except ApiClientError as exc:
    st.error(str(exc))
    st.stop()

if not cases:
    st.info("Create a case and run analysis before asking questions.")
    st.stop()

selected_case = st.selectbox("Case", cases, format_func=case_label)
with st.form("case_question"):
    query = st.text_input("Question", placeholder="What findings mention a loud sound?")
    submitted = st.form_submit_button("Search case findings")

if submitted:
    if not query.strip():
        st.error("Enter a question.")
    else:
        try:
            result = post_json(
                f"/cases/{selected_case['case_id']}/chat",
                json={"query": query},
            )
            st.session_state["chat_result"] = result
        except ApiClientError as exc:
            st.error(str(exc))

if "chat_result" in st.session_state:
    result = st.session_state["chat_result"]
    st.info(result["disclaimer"])
    st.write(result["answer"])
    st.subheader("Evidence citations")
    if not result["citations"]:
        st.caption("No matching findings were returned.")
    for citation in result["citations"]:
        st.markdown(
            f"- **{citation['label']}** — {citation['description']} "
            f"(finding `{citation['finding_id']}`, evidence `{citation['evidence_id']}`)"
        )
