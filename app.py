import streamlit as st

st.title("PDF Generator")

link_type = st.selectbox("Link type", options=["Drive Folder", "Colab File"])

inp_link = st.text_input(f"{link_type} link")

process_btn = st.button("Process link")

if process_btn:
    st.write("button clicked")
    st.write(f"Processing {inp_link}")
