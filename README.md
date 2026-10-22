# scholar-oa

Automated Open-Access Academic Paper Discovery and Downloader.

[![Python](https://img.shields.io/badge/Python-3.8+-161b22?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-161b22?style=flat)](https://opensource.org/licenses/MIT)
[![arXiv API](https://img.shields.io/badge/API-arXiv-161b22?style=flat)](https://arxiv.org/)
[![Open Access](https://img.shields.io/badge/Access-Open_Access-161b22?style=flat)](https://en.wikipedia.org/wiki/Open_access)

scholar-oa is a lightweight, zero-configuration Python utility that discovers and downloads free open-access academic research papers from Google Scholar and arXiv into any destination directory.

---

## Features

- **Dual-Engine Discovery**: Scrapes Google Scholar for open-access preprint links and seamlessly falls back to or augments with the arXiv REST API.
- **Identifier Resolution**: Supports both broad topic search queries and direct arXiv paper identifiers (e.g. `1706.03762`).
- **Filename Sanitization**: Automatically cleans academic titles into standardized, human-readable file paths (`YYYY_Title.pdf`).
- **Integrity Validation**: Verifies standard `%PDF-` file header signatures to ensure incomplete or corrupted downloads are safely rejected.
- **Zero API Keys**: Operates entirely without requiring authenticated tokens or API credentials.

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/MonZenn/scholar-oa.git
cd scholar-oa
pip install -r requirements.txt
```

Alternatively, install as a global CLI tool:

```bash
pip install .
```

---

## AI Agent Skill Installation

`scholar-oa` includes a pre-packaged [`SKILL.md`](SKILL.md) conforming to the Agent Skills standard, enabling autonomous AI coding agents (such as Google Antigravity, Claude Code, OpenAI Codex, Cursor, and Windsurf) to discover and retrieve academic literature directly during research workflows.

### Quick Install by Agent Framework

#### 1. Google Antigravity / Gemini CLI (`agy`)
Install to your global agent skills configuration:
```bash
mkdir -p ~/.gemini/config/skills/scholar-oa
curl -sSL https://raw.githubusercontent.com/MonZenn/scholar-oa/main/SKILL.md -o ~/.gemini/config/skills/scholar-oa/SKILL.md
pip install git+https://github.com/MonZenn/scholar-oa.git
```
*(Or for a project-scoped skill, place `SKILL.md` in `<WORKSPACE_ROOT>/.gemini/skills/scholar-oa/SKILL.md`)*

#### 2. Claude Code (`claude`)
Install to Claude's skill repository:
```bash
mkdir -p ~/.claude/skills/scholar-oa
curl -sSL https://raw.githubusercontent.com/MonZenn/scholar-oa/main/SKILL.md -o ~/.claude/skills/scholar-oa/SKILL.md
pip install git+https://github.com/MonZenn/scholar-oa.git
```

#### 3. OpenAI Codex / Cursor / Windsurf / Universal Agent Standards
Install to the universal agent skills directory (`~/.agents/skills/`):
```bash
mkdir -p ~/.agents/skills/scholar-oa
curl -sSL https://raw.githubusercontent.com/MonZenn/scholar-oa/main/SKILL.md -o ~/.agents/skills/scholar-oa/SKILL.md
pip install git+https://github.com/MonZenn/scholar-oa.git
```

---

## Instructions for Autonomous Agents

If you are an AI assistant or autonomous coding agent instructed to install or configure `scholar-oa` as an active skill in your current runtime environment, execute the following procedure:

1. **Install the CLI package**:
   ```bash
   pip install git+https://github.com/MonZenn/scholar-oa.git
   ```
   *If working locally inside the cloned repository, run `pip install .` instead.*

2. **Deploy the skill definition**:
   Determine which agent environment you are executing in and copy [`SKILL.md`](SKILL.md) to the appropriate destination:
   - **Antigravity / Gemini CLI**: `~/.gemini/config/skills/scholar-oa/SKILL.md`
   - **Claude Code**: `~/.claude/skills/scholar-oa/SKILL.md`
   - **Codex / Universal**: `~/.agents/skills/scholar-oa/SKILL.md`
   - **Workspace Level**: `<WORKSPACE_ROOT>/.agents/skills/scholar-oa/SKILL.md` or `<WORKSPACE_ROOT>/.gemini/skills/scholar-oa/SKILL.md`

3. **Verify CLI availability**:
   ```bash
   scholar-oa --help
   ```

4. **Agent Execution Protocol**:
   When answering user requests to find or download academic papers:
   - Identify the user's topic and requested destination directory (default to `./papers/` if unspecified).
   - Ensure target directory exists: `mkdir -p "<TARGET_DIR>"`.
   - Run: `scholar-oa "<QUERY>" --limit <N> --output-dir "<TARGET_DIR>"`.
   - Verify that retrieved `.pdf` files have valid `%PDF-` header signatures.
   - Summarize retrieved papers in a clean markdown table with Title, Year, Source, and local file paths.

---

## Usage

### Topic Search and Bulk Download

Download the top 5 open-access papers for a query:

```bash
python3 scholar_oa.py "test-time adaptation medical image segmentation"
```

Specify download limits and a custom destination directory:

```bash
python3 scholar_oa.py "thyroid ultrasound deep learning" --limit 10 --output-dir ./research_papers
```

### Direct arXiv Paper Retrieval

Download a specific publication by its arXiv identifier:

```bash
python3 scholar_oa.py --arxiv 1706.03762 --output-dir ./papers
```

### Preview Candidate Results (Dry Run)

Search and inspect titles, authors, and source URLs without downloading PDFs:

```bash
python3 scholar_oa.py "vision transformers" --limit 5 --dry-run
```

---

## Command-Line Options

| Argument | Description | Default |
| :--- | :--- | :--- |
| `query` | Topic search terms or publication title | `""` |
| `-l, --limit` | Maximum number of papers to fetch | `5` |
| `-o, --output-dir` | Target folder for saved PDF documents | `./papers` |
| `--arxiv` | Download specific paper by arXiv ID | `None` |
| `--url` | Download specific PDF directly from URL | `None` |
| `--dry-run` | List candidate papers without writing files | `False` |

---

## Python API Usage

```python
from scholar_oa import search_papers, download_pdf
from pathlib import Path

# Discover open-access papers
papers = search_papers("contrastive learning", limit=3)

# Download each discovered paper
for paper in papers:
    filename = f"{paper['year']}_{paper['title'][:40]}.pdf"
    download_pdf(paper["pdf_url"], Path("./papers") / filename)
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
