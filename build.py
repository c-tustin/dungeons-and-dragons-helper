#!/usr/bin/env python3
"""Bundle app/ into self-contained single HTML files.

  dnd-helper.html        public build, starts with a blank character (committed)
  dnd-helper-party.html  same app with the party from app/party/ preloaded
                         (local only, git-ignored; this is the one to send friends)

Everything (pdf.js, its worker, portraits) is inlined, so each file can be
emailed or AirDropped and opened directly. Usage: python3 build.py
"""
import base64, pathlib, re

ROOT = pathlib.Path(__file__).parent
APP = ROOT / "app"
PARTY = APP / "party" / "party.js"
MIME = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}

def safe(js: str) -> str:
    # A literal "</script" inside inline JS would end the tag early.
    return js.replace("</script", "<\\/script")

def build(out: pathlib.Path, with_party: bool):
    html = (APP / "index.html").read_text()
    pdf = safe((APP / "lib/pdf.min.js").read_text())
    worker = safe((APP / "lib/pdf.worker.min.js").read_text())

    tag = '<script src="lib/pdf.min.js"></script>'
    assert tag in html
    html = html.replace(tag, f"<script>{pdf}</script>\n<script id=\"pdf-worker-src\" type=\"text/plain\">{worker}</script>")

    line = "pdfjsLib.GlobalWorkerOptions.workerSrc = 'lib/pdf.worker.min.js';"
    assert line in html
    html = html.replace(line, "pdfjsLib.GlobalWorkerOptions.workerSrc = URL.createObjectURL(new Blob([document.getElementById('pdf-worker-src').textContent], { type: 'text/javascript' }));")

    party_tag = re.search(r'<script src="party/party.js"></script>[^\n]*', html)
    assert party_tag
    party_js, n = "", 0
    if with_party:
        def inline(m):
            f = APP / m.group(1)
            return '"data:%s;base64,%s"' % (MIME[f.suffix.lower()], base64.b64encode(f.read_bytes()).decode())
        party_js, n = re.subn(r'"(party/portraits/[\w.-]+)"', inline, PARTY.read_text())
        party_js = f"<script>{safe(party_js)}</script>"
    html = html.replace(party_tag.group(0), party_js)

    out.write_text(html)
    print(f"Wrote {out.name} ({out.stat().st_size / 1e6:.1f} MB{f', party + {n} images' if with_party else ', no party'})")

build(ROOT / "dnd-helper.html", with_party=False)
if PARTY.exists():
    build(ROOT / "dnd-helper-party.html", with_party=True)
else:
    print("app/party/party.js not found, so skipped dnd-helper-party.html")
