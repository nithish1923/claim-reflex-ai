from parser import extract_text_from_url

def test_parser():
    url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    text = extract_text_from_url(url)

    assert len(text) > 0
