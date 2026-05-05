import streamlit as st
import json
from datetime import datetime


def render_history_download():
    st.subheader("📂 Chat History")

    if "messages" not in st.session_state or not st.session_state.messages:
        st.info("No chat history yet. Start by asking a question!")
        return

    # Display chat history
    st.write(f"Total messages: {len(st.session_state.messages)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("Download History as JSON"):
            history_data = {
                "exported_at": datetime.now().isoformat(),
                "total_messages": len(st.session_state.messages),
                "messages": st.session_state.messages
            }
            json_str = json.dumps(history_data, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )