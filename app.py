import streamlit as st
import utils as ut
import os
import random
import string
from pathlib import Path


st.title("PDF Generator")


inp_link = st.text_input("Drive folder link")
st.write("Make sure that the link you are sharing is visible by anyone")

process_btn = st.button("Process link")

if process_btn:
    st.write("button clicked")
    st.write(f"Processing {inp_link}")
    files = ut.get_files_from_drive_folder(inp_link)
    uprocid = "".join(
        random.choices(string.ascii_uppercase + string.ascii_lowercase, k=7)
    )
    st.write(f"Unique ID for your processing your request: `{uprocid}`")
    unique_proc_dir = Path(ut.WORK_ROOT) / uprocid
    os.makedirs(ut.WORK_ROOT, exist_ok=True)
    os.mkdir(unique_proc_dir)
    print("Process dir: ", unique_proc_dir)
    st.warning("Do not refresh page, or click any button while in progress")
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)

    # for percent_complete in range(100):
    #     time.sleep(0.1)
    #     my_bar.progress(percent_complete + 1, text=progress_text)
    count = 0
    size = len(files)
    print(size)
    for item in files:
        file_id = item["id"]
        file_name, file_ext = os.path.basename(item["name"]).split(".")
        print(file_name, file_ext)
        if file_ext != "ipynb":
            st.write(f"`{file_name}.{file_ext}` is not a colab file. Skipping")
            continue
        markdown = ut.get_md_from_file(file_name, file_id, usage_dir=unique_proc_dir)
        if not markdown:
            print("Error... could not fetch markdown!")
            continue

        md_path = Path(unique_proc_dir) / f"{file_name}.md"
        pdf_path = Path(unique_proc_dir) / f"{file_name}.pdf"

        ut.write_md(markdown, md_path)
        ut.pandoc_gen_pdf(md_path, pdf_path)
        count += (1 / size)
        my_bar.progress(count, text=f"PDF created for {file_name}")
        os.remove(md_path)
    with st.spinner("Zipping files"):
        zip_path = ut.zip_pdfs(uprocid, unique_proc_dir)
    with open(zip_path, "rb") as file:
        st.download_button(
            "Download Zip", file, file_name=f"PDF_Generated_{uprocid}.zip"
        )
    print(zip_path)
