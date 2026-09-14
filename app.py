import streamlit as st
from openai import OpenAI
import base64

st.set_page_config(
    page_title="Kousar AI",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 17px;
        color: #777;
        margin-bottom: 30px;
    }

    .stChatMessage {
        border-radius: 15px;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">🤖 Kousar AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Your personal AI assistant</div>',
    unsafe_allow_html=True
)

client = OpenAI()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("📎 Add Files")

    photo = st.file_uploader(
        "🖼️ Upload Photo",
        type=["jpg", "jpeg", "png", "webp"]
    )

    camera = st.camera_input("📷 Take a Photo")

    document = st.file_uploader(
        "📄 Upload PDF / Document",
        type=["pdf", "txt", "doc", "docx"]
    )

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Show uploaded file
uploaded_file = photo or camera or document

if uploaded_file:
    st.success(f"Selected: {uploaded_file.name}")

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("💬 Ask Kousar AI anything...")

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        try:
            content = []

            # Text question
            content.append({
                "type": "input_text",
                "text": prompt
            })

            # Image / Camera
            if photo or camera:

                image_file = photo if photo else camera
                image_bytes = image_file.getvalue()

                base64_image = base64.b64encode(
                    image_bytes
                ).decode("utf-8")

                image_type = image_file.type

                content.append({
                    "type": "input_image",
                    "image_url": f"data:{image_type};base64,{base64_image}"
                })

            # PDF / Document
            if document:

                uploaded = client.files.create(
                    file=document,
                    purpose="user_data"
                )

                content.append({
                    "type": "input_file",
                    "file_id": uploaded.id
                })

            response = client.responses.create(
                model="gpt-5.6-luna",
                instructions="""
You are Kousar AI, a friendly and intelligent personal AI assistant.

Your personality:
- Be friendly, helpful, and respectful.
- Explain difficult topics in simple language.
- Give clear and practical answers.
- Be concise unless the user asks for detailed information.
- Help with studying, coding, writing, brainstorming, and everyday questions.
- If the user uploads an image, carefully analyze it.
- If the user uploads a PDF or document, answer questions using its content.
- If you are unsure about something, say so instead of making up information.
""",
                input=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )

            answer = response.output_text

            st.markdown(answer)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

        except Exception as e:
            st.error(f"Error: {e}")