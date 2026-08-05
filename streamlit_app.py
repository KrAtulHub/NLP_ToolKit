import json
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from ner import ner
from sn import sentiment
from TC import text_classification

load_dotenv()

DATABASE_PATH = Path(__file__).parent / "Database.json"

ENTITY_TYPE_MAP = {
    "PER": "Person",
    "ORG": "Organization",
    "LOC": "Location",
    "MISC": "Miscellaneous",
}

ENTITY_BADGE_COLORS = {
    "Person": "violet",
    "Organization": "green",
    "Location": "blue",
    "Miscellaneous": "orange",
}

TC_LABELS = ["Sports", "Politics", "Technology", "Business"]

SAMPLE_TEXTS = {
    "ner": (
        "Barack Obama met Sundar Pichai at Google headquarters in Mountain View "
        "to discuss artificial intelligence policy."
    ),
    "sentiment": (
        "I absolutely love this product! The quality is outstanding and "
        "customer service was incredibly helpful."
    ),
    "tc": (
        "Apple unveiled its latest iPhone featuring a faster chip, improved camera, "
        "and new AI capabilities aimed at mobile users worldwide."
    ),
}

NAV_OPTIONS = [
    "Named Entity Recognition",
    "Sentiment Analysis",
    "Text Classification",
]


def load_database() -> dict:
    try:
        with open(DATABASE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_database(database: dict) -> None:
    with open(DATABASE_PATH, "w", encoding="utf-8") as file:
        json.dump(database, file, indent=4)


def init_session_state() -> None:
    defaults = {
        "logged_in": False,
        "user_name": "",
        "user_email": "",
        "page": NAV_OPTIONS[0],
        "auth_mode": "login",
        "show_registration_success": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def parse_sentiment_result(result) -> dict | None:
    """Support both HF response shapes: [{...}] and [[{...}]]."""
    if isinstance(result, dict) and "label" in result:
        return result

    if isinstance(result, list) and result:
        first = result[0]
        if isinstance(first, dict):
            return first
        if isinstance(first, list) and first and isinstance(first[0], dict):
            return first[0]

    return None


def parse_classification_result(result) -> tuple[list[str], list[float]] | None:
    """Support both HF response shapes: {labels, scores} and [{label, score}]."""
    if isinstance(result, dict) and "labels" in result and "scores" in result:
        return result["labels"], result["scores"]

    if isinstance(result, list) and result and isinstance(result[0], dict) and "label" in result[0]:
        labels = [item["label"] for item in result]
        scores = [float(item["score"]) for item in result]
        return labels, scores

    return None


def render_sample_button(sample_key: str, input_key: str) -> None:
    if st.button("Try sample text", key=f"sample_{sample_key}", use_container_width=True):
        st.session_state[input_key] = SAMPLE_TEXTS[sample_key]
        st.rerun()


def logout() -> None:
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.user_email = ""
    st.session_state.page = NAV_OPTIONS[0]


def merge_ner_entities(raw_entities: list) -> list[dict]:
    merged = []
    previous = None

    for entity in raw_entities:
        word = entity.get("word", "")
        if word.startswith("##"):
            if previous is not None:
                previous["word"] += word.replace("##", "")
            continue

        if previous is not None:
            merged.append(previous)
        previous = dict(entity)

    if previous is not None:
        merged.append(previous)

    return merged


def map_entity_type(entity_group: str) -> str:
    return ENTITY_TYPE_MAP.get(entity_group, entity_group)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            .block-container { padding-top: 1.5rem; max-width: 1100px; }

            div[data-testid="stSidebar"] {
                background-color: var(--secondary-background-color);
            }

            div.stButton > button[kind="primary"] {
                background: linear-gradient(135deg, #4338ca 0%, #0d9488 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
            }
            div.stButton > button[kind="primary"]:hover {
                color: white;
                border: none;
                opacity: 0.92;
            }

            /* Keep result-panel text readable in light and dark themes */
            [data-testid="stVerticalBlockBorderWrapper"] p,
            [data-testid="stVerticalBlockBorderWrapper"] span,
            [data-testid="stVerticalBlockBorderWrapper"] label,
            [data-testid="stVerticalBlockBorderWrapper"] h1,
            [data-testid="stVerticalBlockBorderWrapper"] h2,
            [data-testid="stVerticalBlockBorderWrapper"] h3 {
                color: var(--text-color);
            }

            .result-row {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 0.75rem;
                padding: 0.55rem 0;
                border-bottom: 1px solid color-mix(in srgb, var(--text-color) 15%, transparent);
            }
            .result-row:last-child { border-bottom: none; }
            .result-label {
                font-weight: 600;
                color: var(--text-color);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.title("🧠 NLP Toolkit")
    st.caption("Named Entity Recognition · Sentiment Analysis · Text Classification")


def render_auth_page() -> None:
    render_header()
    st.divider()

    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        if st.session_state.auth_mode == "login":
            if st.session_state.show_registration_success:
                st.success("Registration successful! Please sign in with your email and password.")
                st.session_state.show_registration_success = False

            with st.form("login_form", clear_on_submit=False):
                st.subheader("Sign in")
                login_email = st.text_input("Email", key="login_email")
                login_password = st.text_input("Password", type="password", key="login_password")
                submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

                if submitted:
                    if not login_email.strip() or not login_password.strip():
                        st.warning("Please enter both email and password.")
                    else:
                        database = load_database()
                        email_key = login_email.strip()

                        if email_key not in database:
                            st.error("Email not registered. Please register first.")
                        elif login_password != database[email_key]["password"]:
                            st.error("Wrong password. Please try again.")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.user_name = database[email_key]["name"]
                            st.session_state.user_email = email_key
                            st.rerun()

            st.caption("Don't have an account?")
            if st.button("Create an account", use_container_width=True):
                st.session_state.auth_mode = "register"
                st.rerun()

        else:
            with st.form("register_form", clear_on_submit=True):
                st.subheader("Create account")
                reg_name = st.text_input("Full Name", key="reg_name")
                reg_email = st.text_input("Email", key="reg_email")
                reg_phone = st.text_input("Phone", key="reg_phone")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                submitted = st.form_submit_button("Register", type="primary", use_container_width=True)

                if submitted:
                    if not all([reg_name.strip(), reg_email.strip(), reg_phone.strip(), reg_password.strip()]):
                        st.warning("Please fill in all fields.")
                    else:
                        database = load_database()
                        email_key = reg_email.strip()

                        if email_key in database:
                            st.error("Email already exists. Please login or use a different email.")
                        else:
                            database[email_key] = {
                                "name": reg_name.strip(),
                                "phone": reg_phone.strip(),
                                "password": reg_password,
                            }
                            save_database(database)
                            st.session_state.auth_mode = "login"
                            st.session_state.login_email = email_key
                            st.session_state.show_registration_success = True
                            st.rerun()

            st.caption("Already have an account?")
            if st.button("Back to login", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()


def render_results_panel(title: str = "Results") -> None:
    st.subheader(title)


def render_ner_page() -> None:
    st.subheader("Named Entity Recognition")
    col_input, col_results = st.columns(2, gap="large")

    with col_input:
        with st.container(border=True):
            with st.expander("Sample input", expanded=False):
                st.write(SAMPLE_TEXTS["ner"])
            render_sample_button("ner", "ner_input")
            paragraph = st.text_area(
                "Your text",
                height=240,
                key="ner_input",
                placeholder="Type or paste text here…",
            )
            analyze = st.button("Analyze", type="primary", key="ner_analyze", use_container_width=True)

    with col_results:
        with st.container(border=True):
            render_results_panel()
            if not analyze:
                st.caption("Results will appear here after you analyze.")
            elif not paragraph.strip():
                st.warning("Please enter some text first.")
            else:
                try:
                    with st.spinner("Analyzing…"):
                        raw_result = ner(paragraph.strip())

                    if not isinstance(raw_result, list):
                        st.error(f"Unexpected API response: {raw_result}")
                    elif not raw_result:
                        st.info("No entities found.")
                    else:
                        entities = merge_ner_entities(raw_result)
                        for entity in entities:
                            entity_type = map_entity_type(entity.get("entity_group", ""))
                            word = entity.get("word", "")
                            name_col, badge_col = st.columns([3, 2])
                            with name_col:
                                st.markdown(f"**{word}**")
                            with badge_col:
                                st.badge(
                                    entity_type,
                                    color=ENTITY_BADGE_COLORS.get(entity_type, "gray"), # type: ignore
                                )
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")


def render_sentiment_page() -> None:
    st.subheader("Sentiment Analysis")
    col_input, col_results = st.columns(2, gap="large")

    with col_input:
        with st.container(border=True):
            with st.expander("Sample input", expanded=False):
                st.write(SAMPLE_TEXTS["sentiment"])
            render_sample_button("sentiment", "sentiment_input")
            paragraph = st.text_area(
                "Your text",
                height=240,
                key="sentiment_input",
                placeholder="Type or paste text here…",
            )
            analyze = st.button("Analyze", type="primary", key="sentiment_analyze", use_container_width=True)

    with col_results:
        with st.container(border=True):
            render_results_panel()
            if not analyze:
                st.caption("Results will appear here after you analyze.")
            elif not paragraph.strip():
                st.warning("Please enter some text first.")
            else:
                try:
                    with st.spinner("Analyzing…"):
                        result = sentiment(paragraph.strip())

                    parsed = parse_sentiment_result(result)
                    if parsed is None:
                        st.error(f"Unexpected API response: {result}")
                    else:
                        label = parsed.get("label", "UNKNOWN").upper()
                        score = float(parsed.get("score", 0.0))
                        pct = round(score * 100, 1)

                        if "POS" in label:
                            st.success(f"**{label}** — {pct}% confidence")
                        elif "NEG" in label:
                            st.error(f"**{label}** — {pct}% confidence")
                        else:
                            st.info(f"**{label}** — {pct}% confidence")

                        st.progress(min(max(score, 0.0), 1.0))
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")


def render_classification_page() -> None:
    st.subheader("Text Classification")
    col_input, col_results = st.columns(2, gap="large")

    with col_input:
        with st.container(border=True):
            with st.expander("Sample input", expanded=False):
                st.write(SAMPLE_TEXTS["tc"])
            render_sample_button("tc", "tc_input")
            paragraph = st.text_area(
                "Your text",
                height=240,
                key="tc_input",
                placeholder="Type or paste text here…",
            )
            analyze = st.button("Analyze", type="primary", key="tc_analyze", use_container_width=True)

    with col_results:
        with st.container(border=True):
            render_results_panel()
            if not analyze:
                st.caption("Results will appear here after you analyze.")
            elif not paragraph.strip():
                st.warning("Please enter some text first.")
            else:
                try:
                    with st.spinner("Analyzing…"):
                        result = text_classification(paragraph.strip(), TC_LABELS)

                    parsed = parse_classification_result(result)
                    if parsed is None:
                        st.error(f"Unexpected API response: {result}")
                    else:
                        labels, scores = parsed
                        top_label = labels[0]
                        top_pct = round(float(scores[0]) * 100, 1)
                        st.metric("Top category", top_label, f"{top_pct}%")

                        chart_df = pd.DataFrame({"Score": scores}, index=labels)
                        st.bar_chart(chart_df, horizontal=True, color="#0d9488")
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")


def render_main_app() -> None:
    with st.sidebar:
        st.markdown(f"**{st.session_state.user_name}**")
        st.caption(st.session_state.user_email)
        st.divider()

        page = st.radio(
            "Tools",
            NAV_OPTIONS,
            index=NAV_OPTIONS.index(st.session_state.page)
            if st.session_state.page in NAV_OPTIONS
            else 0,
            label_visibility="collapsed",
        )
        st.session_state.page = page

        st.divider()
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

    render_header()
    st.divider()

    if page == "Named Entity Recognition":
        render_ner_page()
    elif page == "Sentiment Analysis":
        render_sentiment_page()
    else:
        render_classification_page()


def main() -> None:
    st.set_page_config(
        page_title="NLP Toolkit",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_session_state()
    apply_theme()

    if st.session_state.logged_in:
        render_main_app()
    else:
        render_auth_page()


if __name__ == "__main__":
    main()
