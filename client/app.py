import streamlit as st
import requests
from components.upload import render_upload
from components.chatUI import render_chat
from components.history_download import render_history_download


st.set_page_config(page_title="Medical AI Assistant", page_icon=":hospital:", layout="centered")
st.title("Medical AI Assistant")
st.write("Upload your medical documents and ask questions to get insights!")

with st.sidebar:
    st.markdown("## 📤 Upload to Database")
    render_upload()

st.markdown("---")
render_chat()
st.markdown("---")
render_history_download()
