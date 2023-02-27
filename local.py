import requests
import hashlib
from pathlib import Path

curr_path = Path(__file__).resolve()
html_dump_path = curr_path.parent / "html_dump"

def get_html(url):
    md5 = hashlib.md5(url.encode('utf-8')).hexdigest()
    file_path = html_dump_path / f"{md5}.html"
    if file_path.exists():
        print(f"reading saved copy of {url}")
        with file_path.open('r') as file:
            html = file.read()
        is_found = True
    else:
        print(f"making request to {url}")
        res = requests.get(url)
        assert res.status_code == 200
        html = res.text
        with file_path.open('w') as file:
            file.write(html)
        is_found = False
    return html, is_found
