"""Offline PDF extraction with page evidence; not an LC compliance decision."""
import argparse
import json
from pathlib import Path

MAX_BYTES = 25_000_000
MAX_PAGES = 100


def inspect_pdf(path):
    import fitz
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Missing or oversized PDF")
    with fitz.open(path) as pdf:
        if pdf.needs_pass or len(pdf) > MAX_PAGES or not pdf.is_pdf:
            raise ValueError("Encrypted, oversized, or invalid PDF")
        pages = []
        for i, page in enumerate(pdf):
            text = page.get_text("text").strip()
            pages.append({"page": i + 1, "text": text[:12000], "requires_manual_review": not bool(text)})
    return {"document": path.name, "pages": pages, "status": "NEEDS_REVIEW"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inspect_pdf(args.pdf)
    if args.output:
        try:
            with args.output.open("x", encoding="utf-8") as report:
                json.dump(result, report, ensure_ascii=False, indent=2)
        except FileExistsError:
            parser.error("Refusing to overwrite an existing report")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
