#!/usr/bin/env python3
"""
scholar-oa: Automated Open-Access Academic Paper Discovery and Downloader

Retrieves free, open-access academic research PDFs from Google Scholar and
the arXiv REST API. Supports keyword search, direct arXiv identifier fetching,
title-based filename sanitization, and PDF magic-byte validation.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_USER_AGENT = "scholar-oa/0.1.0 (+https://github.com/MonZenn/scholar-oa)"


def sanitize_filename(name: str, max_length: int = 80) -> str:
    """Sanitize title into a safe, cross-platform filename."""
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip()
    return cleaned or "paper"


def is_valid_pdf(file_path: Path) -> bool:
    """Validate that the target file begins with the standard %PDF magic header."""
    if not file_path.is_file() or file_path.stat().st_size < 100:
        return False
    try:
        with file_path.open("rb") as f:
            header = f.read(5)
            return header.startswith(b"%PDF-")
    except OSError:
        return False


def query_arxiv(query: str, limit: int = 5) -> List[Dict[str, str]]:
    """Query the unauthenticated arXiv REST API for open-access papers."""
    results: List[Dict[str, str]] = []
    encoded_query = urllib.parse.quote(query)
    url = (
        f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}"
        f"&start=0&max_results={limit}&sortBy=relevance"
    )

    req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            tree = ET.fromstring(response.read())
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in tree.findall("atom:entry", ns):
                title_elem = entry.find("atom:title", ns)
                title = (
                    title_elem.text.strip().replace("\n", " ")
                    if title_elem is not None and title_elem.text
                    else "Unknown Title"
                )
                id_elem = entry.find("atom:id", ns)
                id_url = id_elem.text.strip() if id_elem is not None and id_elem.text else ""
                arxiv_id = id_url.split("/abs/")[-1]

                published_elem = entry.find("atom:published", ns)
                year = (
                    published_elem.text[:4]
                    if published_elem is not None and published_elem.text
                    else "Recent"
                )

                if arxiv_id:
                    results.append({
                        "title": title,
                        "year": year,
                        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                        "source": "arXiv",
                        "id": arxiv_id,
                    })
    except Exception as err:
        sys.stderr.write(f"arXiv query warning: {err}\n")

    return results


def query_google_scholar(query: str, limit: int = 5) -> List[Dict[str, str]]:
    """Query Google Scholar via the scholarly library if available."""
    results: List[Dict[str, str]] = []
    try:
        from scholarly import scholarly

        search_query = scholarly.search_pubs(query)
        for _ in range(limit):
            try:
                pub = next(search_query)
                bib = pub.get("bib", {})
                title = bib.get("title", "Unknown Title")
                year = str(bib.get("pub_year", "N/A"))
                eprint_url = pub.get("eprint_url")

                if eprint_url:
                    results.append({
                        "title": title,
                        "year": year,
                        "pdf_url": eprint_url,
                        "source": "Google Scholar",
                        "id": "",
                    })
            except StopIteration:
                break
    except ImportError:
        pass
    except Exception as err:
        sys.stderr.write(f"Google Scholar query notice: {err}\n")

    return results


def search_papers(query: str, limit: int = 5) -> List[Dict[str, str]]:
    """Dual-discovery search: attempts Google Scholar first, then fills/augments via arXiv."""
    papers = query_google_scholar(query, limit=limit)
    if len(papers) < limit:
        needed = limit - len(papers)
        arxiv_papers = query_arxiv(query, limit=needed)
        papers.extend(arxiv_papers)
    return papers[:limit]


def download_pdf(url: str, dest_path: Path) -> bool:
    """Download a PDF using a standard User-Agent header, verifying the PDF magic bytes."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as response, dest_path.open("wb") as out_file:
            while chunk := response.read(65536):
                out_file.write(chunk)

        if not is_valid_pdf(dest_path):
            if dest_path.exists():
                dest_path.unlink()
            return False
        return True
    except Exception as err:
        sys.stderr.write(f"Failed to download {url}: {err}\n")
        if dest_path.exists():
            dest_path.unlink()
        return False


def download_arxiv_id(arxiv_id: str, output_dir: Path) -> Optional[Path]:
    """Download an academic paper directly by arXiv identifier."""
    clean_id = re.sub(r"^arxiv:", "", arxiv_id, flags=re.IGNORECASE).strip()
    pdf_url = f"https://arxiv.org/pdf/{clean_id}.pdf"
    target_path = output_dir / f"{clean_id}.pdf"
    if download_pdf(pdf_url, target_path):
        return target_path
    return None


def format_bytes(size: int) -> str:
    """Format bytes into human-readable representation."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="scholar-oa: Automated Open-Access Academic Paper Downloader"
    )
    parser.add_argument("query", nargs="?", default="", help="Search query or research topic")
    parser.add_argument("-l", "--limit", type=int, default=5, help="Maximum number of papers to fetch (default: 5)")
    parser.add_argument("-o", "--output-dir", default="./papers", help="Output directory path (default: ./papers)")
    parser.add_argument("--arxiv", default="", help="Direct arXiv ID download (e.g. 1706.03762)")
    parser.add_argument("--url", default="", help="Direct PDF URL to download")
    parser.add_argument("--dry-run", action="store_true", help="Search and list papers without downloading")

    args = parser.parse_args()
    out_dir = Path(args.output_dir).expanduser().resolve()

    # Case 1: Direct arXiv ID
    if args.arxiv:
        print(f"Downloading arXiv ID: {args.arxiv} -> {out_dir}")
        path = download_arxiv_id(args.arxiv, out_dir)
        if path:
            print(f"Success: {path.name} ({format_bytes(path.stat().st_size)})")
            return 0
        else:
            print("Failed to download paper from arXiv.")
            return 1

    # Case 2: Direct URL
    if args.url:
        print(f"Downloading direct URL: {args.url} -> {out_dir}")
        filename = sanitize_filename(Path(urllib.parse.urlparse(args.url).path).stem) + ".pdf"
        target = out_dir / filename
        if download_pdf(args.url, target):
            print(f"Success: {target.name} ({format_bytes(target.stat().st_size)})")
            return 0
        else:
            print("Failed to download PDF from URL.")
            return 1

    # Case 3: Topic Search
    query = args.query.strip()
    if not query:
        parser.print_help()
        return 1

    print(f"Searching open-access repositories for: \"{query}\" (limit: {args.limit})")
    papers = search_papers(query, limit=args.limit)

    if not papers:
        print("No open-access papers found matching query.")
        return 0

    print(f"Found {len(papers)} candidate paper(s).\n")

    if args.dry_run:
        for idx, p in enumerate(papers, 1):
            print(f"[{idx}] {p['year']} | {p['title']}")
            print(f"    Source: {p['source']} | URL: {p['pdf_url']}")
        return 0

    downloaded = []
    for idx, p in enumerate(papers, 1):
        clean_title = sanitize_filename(p["title"])
        year_prefix = f"{p['year']}_" if p["year"] != "N/A" else ""
        filename = f"{year_prefix}{clean_title}.pdf"
        target_path = out_dir / filename

        print(f"[{idx}/{len(papers)}] Downloading: {p['title'][:65]}...")
        if download_pdf(p["pdf_url"], target_path):
            size_str = format_bytes(target_path.stat().st_size)
            print(f"       Saved: {target_path.name} ({size_str})")
            downloaded.append((p["title"], p["year"], p["source"], target_path.name, size_str))
        else:
            print(f"       Failed to retrieve PDF.")

    print("\n" + "=" * 80)
    print(f"Download Summary: {len(downloaded)}/{len(papers)} papers successfully saved to {out_dir}")
    print("=" * 80)
    for title, yr, src, fname, sz in downloaded:
        print(f"- {fname} [{sz}] ({src}, {yr})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
