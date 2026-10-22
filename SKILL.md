---
name: scholar-oa
description: Discovers academic research papers from Google Scholar and open-access repositories (arXiv/preprints), resolves free full-text PDFs, and downloads them to a user-specified destination folder. Use whenever the user asks to search, retrieve, or download academic papers.
---

# scholar-oa: Academic Paper Discovery & Downloader

Automated agent skill for discovering, resolving, and downloading open-access academic research papers from Google Scholar and arXiv into any target workspace directory.

## Core Capabilities

- **Topic Discovery**: Queries Google Scholar for open-access preprint links and seamlessly augments or falls back to the arXiv REST API.
- **Identifier Retrieval**: Resolves direct arXiv identifiers (e.g., `1706.03762`) or direct PDF URLs.
- **File Sanitization**: Cleans paper titles into safe, standardized filenames (`YYYY_Title.pdf`).
- **Integrity Validation**: Verifies the standard `%PDF-` magic byte header to guarantee valid PDF payloads.
- **Zero Credentials**: Operates out-of-the-box without requiring API keys or authentication tokens.

---

## Agent Execution Instructions

### 1. Resolve Target Directory
- Extract the desired destination directory from the user prompt (e.g., `./papers`, `~/Documents/Thesis/literature`, `./research`).
- If no destination directory is specified by the user, default to `./papers/`.
- Always ensure the directory exists prior to download:
  ```bash
  mkdir -p "<TARGET_DIR>"
  ```

### 2. Run Retrieval Command
Execute the CLI tool in your shell environment:

**Broad Topic Search**:
```bash
scholar-oa "<SEARCH_QUERY>" --limit <LIMIT> --output-dir "<TARGET_DIR>"
```

**Direct arXiv Identifier**:
```bash
scholar-oa --arxiv "<ARXIV_ID>" --output-dir "<TARGET_DIR>"
```

**Direct PDF URL**:
```bash
scholar-oa --url "<PDF_URL>" --output-dir "<TARGET_DIR>"
```

*Note: If `scholar-oa` is not installed on PATH, run via Python directly:*
```bash
python3 /path/to/scholar-oa/scholar_oa.py "<SEARCH_QUERY>" --limit <LIMIT> --output-dir "<TARGET_DIR>"
```

### 3. Verify & Report Results
- Confirm that the downloaded files exist on disk and possess non-zero file sizes.
- Output a structured Markdown table summarizing the retrieved papers:
  - **Title**
  - **Year & Source** (Google Scholar / arXiv)
  - **Local File Path**
  - **File Size**
