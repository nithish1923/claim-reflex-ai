import requests
import tempfile
import fitz   # PyMuPDF

def extract_text_from_url(url):

    response = requests.get(url)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name

    text = ""

    doc = fitz.open(tmp_path)

    for page in doc:
        text += page.get_text()

    doc.close()

    return text
