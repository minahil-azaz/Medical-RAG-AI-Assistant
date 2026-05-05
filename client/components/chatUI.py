import streamlit as st
from utlis.api import ask_question


def render_chat():
    st.subheader("🩺 Ask Questions About Your Medical Documents")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # -------------------------
    # Render chat history
    # -------------------------
    for message in st.session_state.messages:
        with st.chat_message("user" if message["is_user"] else "assistant"):
            st.markdown(message["content"])

    # -------------------------
    # User input
    # -------------------------
    user_input = st.chat_input("Type your question here...")

    if user_input:
        # Add user message
        st.session_state.messages.append({
            "content": user_input,
            "is_user": True
        })

        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)

        # Call backend
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = ask_question(user_input)

                    if "error" in response:
                        answer = f"❌ Error: {response['error']}"
                    else:
                        answer = response.get("response", "No response received.")
                        sources = response.get("sources", [])
                        
                        # Display sources if available
                        if sources and sources[0]:  # Check if sources list is not empty
                            answer += "\n\n**Sources:**\n" + "\n".join([f"- {s}" for s in sources if s])
                    
                    st.markdown(answer)

                    # Save assistant response
                    st.session_state.messages.append({
                        "content": answer,
                        "is_user": False
                    })

                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.markdown(error_msg)

                    st.session_state.messages.append({
                        "content": error_msg,
                        "is_user": False
                    })