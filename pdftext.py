"""Dump a PDF to plain text next to the source file. Usage: python pdftext.py <pdf> [...]"""
import sys, pathlib
import fitz

for arg in sys.argv[1:]:
    src = pathlib.Path(arg)
    doc = fitz.open(src)
    out = src.with_suffix(".txt")
    chunks = []
    for i, page in enumerate(doc, 1):
        chunks.append(f"\n\n=== [page {i}] ===\n{page.get_text()}")
    out.write_text("".join(chunks), encoding="utf-8")
    print(f"{src.name}: {doc.page_count} pages -> {out.name} ({out.stat().st_size:,} bytes)")
