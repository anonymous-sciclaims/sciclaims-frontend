"""
A simple streamlit app
run the app by installing streamlit with pip and typing
> streamlit run demo.py
"""

import configparser
import streamlit as st
from pathlib import Path
import pandas as pd
import srsly
import os

from api import claim_analysis


def change_css():
    hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """
    long_buttons = """
            <style>
            div.stButton > button:first-child {
                width:100%;
            }
            div.stButton > button:hover {
                width:100%;
                }
            </style>"""
    big_font = """
    <style>
    .big-font {
        font-size:32px;
    }
    </style>
    """
    m_font = """
        <style>
        .m-font {
            font-size:18px;
        }
        </style>
        """

    big_expander = """
        <style>
        div[data-testid="stExpander"] div[role="button"] p {
            font-size: 24px;
        }
        </style>
        """

    confidence_bar = """
    <style>
    .confidencebar {
        width: 20%;
        margin-bottom: 15px;
        background-color: #ddd;
    }

    .confidence {
        text-align: center;
        padding-top: 5px;
        padding-bottom: 5px;
        color: white;
    }
    </style>
    """

    # Inject CSS with Markdown
    st.markdown(long_buttons, unsafe_allow_html=True)
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    st.markdown(big_font, unsafe_allow_html=True)
    st.markdown(m_font, unsafe_allow_html=True)
    st.markdown(big_expander, unsafe_allow_html=True)
    st.markdown(confidence_bar, unsafe_allow_html=True)


def write_intro(cfg):
    res_dir = Path(cfg["data"]["res_dir"])

    title = "SciClaims: Biomedical Scientific Claim Verification"
    # PAGE FORMATTING
    st.set_page_config(
        page_title=title,
        layout="wide",
        page_icon=str(res_dir.joinpath("favicon-1.png")),
    )

    # LOGO
    col1, _, col2 = st.columns([1.25, 0.25, 0.5])
    # TITLE
    col1.title(title)
    col2.write("##")
    st.write(" --- ")


def get_spans(evidence_sentences, evidence_text):
    starts = []
    ends = []
    for sent in evidence_sentences:
        start = evidence_text.find(sent)
        if start >= 0:
            starts.append(start)
            ends.append(start + len(sent))
    return sorted(starts), sorted(ends)


def get_highlighted_text(starts, ends, text, label_color):
    new_text = ""
    for i, t in enumerate(text):
        if i in starts:
            new_text = (
                new_text
                + " <span style='color:white;background-color:"
                + label_color
                + "; border-radius:.25rem;padding:.2em'>"
            )
        if i in ends:
            new_text = new_text + "</span> "
        new_text = new_text + t
    return new_text


def get_bg_color(claim_response):
    if claim_response == "SUPPORT":
        return "green"
    else:
        return "red"


def write_body(cfg):
    s = st.session_state
    if "pressed_button" not in s:
        s["pressed_button"] = False
    change_css()
    pd.options.display.float_format = "{:,.2f}".format
    st.markdown(
        '<p class="big-font">Select one of the sample documents below or try your own text. Then, click <b>ANALYZE</b>',
        unsafe_allow_html=True,
    )
    examples = srsly.read_json(os.path.join(cfg["data"]["res_dir"], "examples.json"))

    selection_1 = st.selectbox(
        "",
        [
            "Example "
            + str(x["id"])
            + " ("
            + x["topic"]
            + "-"
            + x["source_type"]
            + "): "
            + x["title"]
            for x in examples
        ],
        key=1,
    )
    selected_id = int(selection_1.split(":")[0].split()[1])
    doc_source = str([x["doc_source"] for x in examples if x["id"] == selected_id][0])
    st.markdown("*[source](" + doc_source + ")*")
    text = st.text_area(
        "",
        [x["text"] for x in examples if x["id"] == selected_id][0],
        max_chars=10000,
        height=210,
    )

    run_button = st.button("Analyze")

    if run_button or s["pressed_button"]:
        s["pressed_button"] = True
        anns = claim_analysis(cfg, text)
        st.markdown(
            '<p class="big-font" style="text-align: center;">&#128202; <b>CLAIM ANALYSIS</b>',
            unsafe_allow_html=True,
        )
        for claim_dict in anns:
            with st.expander(claim_dict["claim"]):
                for claim_rep in claim_dict["claim_analysis"]:
                    st.divider()
                    col1, col2 = st.columns(2)
                    bg_color = get_bg_color(claim_rep["report"]["response"])
                    col1.write(f":large_{bg_color}_square: <b>{claim_rep['report']['response']}</b>", unsafe_allow_html=True)
                    col1.write(f"""
                    <b>Prediction score: </b>
                    <div class="confidencebar">
                        <div class="confidence" style="width: {claim_rep["report"]["confidence"]}%; background: {bg_color};">
                                {claim_rep["report"]["confidence"]}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    col1.markdown(
                        f'<p class="m-font"><b>Rationale</b>: {claim_rep["report"]["rationale"]}',
                        unsafe_allow_html=True,
                    )
                    col1.write(f"https://doi.org/{claim_rep['original_id']}")
                    col2.write(f"{claim_rep['title']}")
                    starts, ends = get_spans(evidence_text=claim_rep['abstract'], evidence_sentences=claim_rep['report']['evidence'])
                    hl_text = get_highlighted_text(starts=starts, ends=ends, text=claim_rep['abstract'], label_color=bg_color)
                    col2.write(f"{hl_text}", unsafe_allow_html=True,)


def main(cfg):
    write_intro(cfg)
    write_body(cfg)


if __name__ == "__main__":
    cfg = configparser.ConfigParser()
    cfg.read("config.ini")
    main(cfg=cfg)
