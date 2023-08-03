import os
import random
import string
from pathlib import Path
from urllib.parse import urlparse

import nbformat
import requests
from decouple import config

API_KEY = config("API_KEY", cast=str)
LATEX_TEMPLATE_PATH = config("LATEX_TEMPLATE_PATH")
WORK_ROOT = "work"


def download_file(url, destination) -> bool:
    print(f"Trying to download {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(response.status_code)
        print(response.content)
        return False
    with open(destination, "wb") as f:
        f.write(response.content)
    return True


def ipynb1md(fpath):
    """Extract the first markdown cell from ipynb"""
    with open(fpath, "r") as f:
        notebook_content = nbformat.read(f, as_version=4)

    first_cell = notebook_content.cells[0]
    if first_cell.cell_type == "markdown":
        return first_cell.source

    return None


def get_md_from_file(file_name, file_id, usage_dir) -> str:
    """Returns markdown from the given file_name and file_id of colab file in g-drive"""
    file_download_url = (
        f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={API_KEY}"
    )
    temp_file_path = Path(usage_dir) / f"{file_name}.ipynb"
    status = download_file(file_download_url, temp_file_path)
    if not status:
        print("Failed to download file! ")
        return None
    markdown_content = ipynb1md(temp_file_path)
    os.remove(temp_file_path)
    return markdown_content


def write_md(md_content, dest_path):
    with open(dest_path, "w") as file:
        file.write(md_content)


def pandoc_gen_pdf(md_path, pdf_path):
    os.system(f"pandoc {md_path} -o {pdf_path} --template={LATEX_TEMPLATE_PATH}")


def zip_pdfs(zip_name, parent_dir) -> str:
    os.system(f"cd {parent_dir} && zip {zip_name}.zip *.pdf")
    return Path(parent_dir) / f"{zip_name}.zip"


def extract_last_path_param(url):
    parsed_url = urlparse(url)
    path = parsed_url.path.strip("/").split("/")
    last_path_parameter = path[-1] if path else None
    return last_path_parameter


def get_files_from_drive_folder(folder_link: str):
    """Return list of {id: ..., name: ... } from google drive public folder link"""
    folder_id = extract_last_path_param(folder_link)
    files_response = requests.get(
        f"https://www.googleapis.com/drive/v3/files?q='{folder_id}'+in+parents&fields=files(id,name)&key={API_KEY}"
    )
    print(files_response.status_code)
    print(files_response.content)
    files_data = files_response.json()
    return files_data["files"]


def main():
    folder_link = config("FOLDER_LINK_TEST")
    print(f"Folder Link: {folder_link}")
    files_data = get_files_from_drive_folder(folder_link)
    print(files_data)
    input("continue ?")
    uprocid = "".join(
        random.choices(string.ascii_uppercase + string.ascii_lowercase, k=7)
    )
    unique_proc_dir = Path(WORK_ROOT) / uprocid
    os.makedirs(WORK_ROOT, exist_ok=True)
    os.mkdir(unique_proc_dir)
    print("Process dir: ", unique_proc_dir)

    for file_info in files_data:
        file_id = file_info["id"]
        file_name, file_ext = os.path.basename(file_info["name"]).split(".")
        if file_ext != ".ipynb":
            continue
        markdown = get_md_from_file(file_name, file_id, usage_dir=unique_proc_dir)
        if not markdown:
            print("Error... could not fetch markdown!")
            continue

        md_path = Path(unique_proc_dir) / f"{file_name}.md"
        pdf_path = Path(unique_proc_dir) / f"{file_name}.pdf"

        write_md(markdown, md_path)
        pandoc_gen_pdf(md_path, pdf_path)
        os.remove(md_path)
    zip_path = zip_pdfs(uprocid, unique_proc_dir)
    print(zip_path)


if __name__ == "__main__":
    main()
