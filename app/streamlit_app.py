import streamlit as st
import requests

st.set_page_config(page_title="Local File Search", layout="wide")
st.title("Local File Search")

api_base = st.text_input("API Base URL", value="http://127.0.0.1:8000")
index_path = st.text_input("Index path", value=".")
web_url = st.text_input("Web URL", value="")

if st.button("Index local path"):
    try:
        response = requests.post(f"{api_base}/index", json={"path": index_path}, timeout=60)
        response.raise_for_status()
        st.success(f"Indexed local docs: {response.json()['indexed']}")
    except requests.RequestException as exc:
        st.error(f"Index failed: {exc}")

if st.button("Index web URL") and web_url.strip():
    try:
        response = requests.post(f"{api_base}/index/web", json={"url": web_url}, timeout=60)
        response.raise_for_status()
        st.success(f"Indexed web docs: {response.json()['indexed']}")
    except requests.RequestException as exc:
        st.error(f"Web index failed: {exc}")

query = st.text_input("Search query")
if st.button("Search") and query.strip():
    try:
        response = requests.post(f"{api_base}/search", json={"query": query, "limit": 20}, timeout=30)
        response.raise_for_status()
        for row in response.json():
            st.subheader(row["path"])
            st.caption(f"rank: {row['rank']}")
            st.write(row["content"])
    except requests.RequestException as exc:
        st.error(f"Search failed: {exc}")
