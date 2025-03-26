import json
import requests
import streamlit as st


@st.cache_data
def claim_analysis(_cfg, text):
    endpoint = _cfg["api"]["claims"]
    response = requests.request(
        "POST",
        endpoint,
        data=text.encode("utf-8"),
        headers={"Content-type": "text/plain; charset=utf-8"},
        verify=False,
    )
    result = response.json()
    return result

