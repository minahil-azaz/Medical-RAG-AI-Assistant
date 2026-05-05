import streamlit as st
from utlis.api import upload_pdf


def render_upload():
    st.subheader("📤 Upload Medical Documents")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        accept_multiple_files=False
    )

    # Show selected file
    if uploaded_file:
        st.write(f"📄 Selected file: {uploaded_file.name}")

        if st.button("Upload to Database"):
            with st.spinner("Uploading and processing..."):
                try:
                    response = upload_pdf(uploaded_file)

                    if "error" in response:
                        st.error(f"❌ Upload failed: {response['error']}")
                    elif response.get("message"):
                        st.success(f"✅ {response['message']}")
                        st.balloons()
                    else:
                        st.success("✅ File uploaded and processed successfully!")
                        st.balloons()

                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")

    else:
        st.info("Please upload a PDF file.")