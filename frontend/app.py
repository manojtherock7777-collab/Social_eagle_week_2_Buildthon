import streamlit as st
import requests


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Tamil Nadu Farmers AI Assistant",
    page_icon="🌾",
    layout="wide"
)


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

API_URL = "http://127.0.0.1:8000"


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 32px;
        font-weight: bold;
        color: #2E7D32;
    }

    .subtitle {
        font-size: 16px;
        color: #666666;
    }

    .stButton button {
        border-radius: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">'
    '🌾 Tamil Nadu Farmers AI Assistant'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your intelligent assistant for Tamil Nadu '
    'government farmer welfare schemes'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("🌱 Farmer Assistant")

    # ----------------------------------------------
    # LANGUAGE SELECTION
    # ----------------------------------------------

    st.markdown("### Language")

    language = st.selectbox(
        "Select your preferred language",
        ["English", "தமிழ்"]
    )

    st.divider()

    # ----------------------------------------------
    # UPLOADED PDF DOCUMENTS
    # ----------------------------------------------

    st.markdown("### 📚 Uploaded Documents")

    if st.button(
        "🔄 Refresh PDF List",
        use_container_width=True
    ):
        st.rerun()

    try:

        pdf_response = requests.get(
            f"{API_URL}/uploaded-pdfs",
            timeout=15
        )

        pdf_response.raise_for_status()

        pdf_data = pdf_response.json()

        if pdf_data.get("success"):

            total_files = pdf_data.get("total_files", 0)

            pdf_files = pdf_data.get("files", [])

            st.metric(
                label="Total PDFs",
                value=total_files
            )

            if pdf_files:

                for index, pdf in enumerate(pdf_files, start=1):

                    with st.expander(
                        f"📄 {pdf['filename']}"
                    ):

                        st.write(
                            f"**File size:** {pdf['size_mb']} MB"
                        )

                        st.write(
                            f"**Uploaded:** {pdf['uploaded_at']}"
                        )

            else:

                st.info(
                    "No PDF documents found in the backend."
                )

        else:

            st.warning(
                "Unable to retrieve the PDF list."
            )

    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to FastAPI. "
            "Please start the backend server."
        )

    except requests.exceptions.Timeout:

        st.error(
            "PDF list request timed out."
        )

    except requests.exceptions.RequestException as error:

        st.error(
            f"Unable to load PDF list: {error}"
        )

    except ValueError:

        st.error(
            "Backend returned an invalid PDF list response."
        )

    st.divider()

    # ----------------------------------------------
    # ABOUT
    # ----------------------------------------------

    st.markdown("### About")

    st.info(
        "This AI assistant helps farmers understand "
        "Tamil Nadu government welfare schemes, "
        "subsidies and benefits using uploaded documents."
    )

    # ----------------------------------------------
    # CLEAR CHAT
    # ----------------------------------------------

    if st.button(
        "Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.caption(
        "Powered by LangChain, OpenAI, FAISS and FastAPI"
    )


# --------------------------------------------------
# CHAT INTERFACE
# --------------------------------------------------

st.subheader("💬 Ask Your Question")


# Display existing conversation

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            sources = message.get("sources", [])

            if sources:

                with st.expander("📚 View Sources"):

                    for source in sources:

                        st.markdown(
                            f"**File:** "
                            f"{source.get('source', 'Unknown')}"
                        )

                        st.markdown(
                            f"**Page:** "
                            f"{source.get('page', 'Unknown')}"
                        )

                        st.divider()


# --------------------------------------------------
# USER INPUT
# --------------------------------------------------

if language == "தமிழ்":

    placeholder = (
        "உங்கள் விவசாயத் திட்டம் தொடர்பான "
        "கேள்வியைக் கேளுங்கள்..."
    )

else:

    placeholder = (
        "Ask about farmer schemes, subsidies or benefits..."
    )


user_question = st.chat_input(placeholder)


# --------------------------------------------------
# PROCESS USER QUESTION
# --------------------------------------------------

if user_question:

    # Display user question

    st.session_state.messages.append({

        "role": "user",
        "content": user_question

    })

    with st.chat_message("user"):

        st.markdown(user_question)

    # Generate assistant response

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching government scheme documents..."
        ):

            try:

                response = requests.post(

                    f"{API_URL}/chat",

                    json={
                        "question": user_question,
                        "language": language
                    },

                    timeout=120

                )

                response.raise_for_status()

                result = response.json()

                if result.get("success"):

                    answer = result.get(
                        "answer",
                        "No answer received."
                    )

                    sources = result.get(
                        "sources",
                        []
                    )

                    st.markdown(answer)

                    if sources:

                        with st.expander("📚 View Sources"):

                            for source in sources:

                                st.markdown(
                                    f"**File:** "
                                    f"{source.get('source', 'Unknown')}"
                                )

                                st.markdown(
                                    f"**Page:** "
                                    f"{source.get('page', 'Unknown')}"
                                )

                                st.divider()

                    st.session_state.messages.append({

                        "role": "assistant",
                        "content": answer,
                        "sources": sources

                    })

                else:

                    error_message = result.get(
                        "answer",
                        "Unable to process your question."
                    )

                    st.error(error_message)

                    st.session_state.messages.append({

                        "role": "assistant",
                        "content": error_message,
                        "sources": []

                    })

            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to FastAPI backend. "
                    "Please check whether the backend is running."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out. Please try again."
                )

            except requests.exceptions.HTTPError as error:

                st.error(
                    f"Backend HTTP error: {error}"
                )

            except requests.exceptions.RequestException as error:

                st.error(
                    f"Request failed: {error}"
                )

            except ValueError:

                st.error(
                    "The backend returned an invalid response."
                )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Tamil Nadu Farmers Welfare Schemes AI Assistant | "
    "Information is based on available reference documents. "
    "Please verify scheme details with the concerned government department."
)