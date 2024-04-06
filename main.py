from fastapi import FastAPI
from pydantic import BaseModel
import requests
import pdfplumber
import re

app = FastAPI()

class PDFLink(BaseModel):
    link: str

@app.get("/")
async def root():
    return {"greeting": "Hello, World!", "message": "Welcome to FastAPI!"}

@app.post("/extract_text_dropboxlink")
async def extract_text_from_pdf(pdf_link: PDFLink):
    # Extract the file ID from the Dropbox link
    dropbox_link = pdf_link.link
    file_id_match = re.search(r"/s/([a-zA-Z0-9]+)/", dropbox_link)
    
    if not file_id_match:
        return {"error": "Invalid Dropbox link"}

    file_id = file_id_match.group(1)
    download_url = f"https://www.dropbox.com/s/{file_id}?raw=1"

    # Download the PDF file from the modified Dropbox link
    response = requests.get(download_url)
    if response.status_code != 200:
        return {"error": "Failed to download PDF"}

    # Save the downloaded PDF to a temporary file
    with open("temp.pdf", "wb") as pdf_file:
        pdf_file.write(response.content)

    # Extract text from the PDF using pdfplumber
    text = ""
    with pdfplumber.open("temp.pdf") as pdf:
        for page in pdf.pages:
            text += page.extract_text()

    # Clean up: delete the temporary file
    import os
    os.remove("temp.pdf")

    return {"text": text}