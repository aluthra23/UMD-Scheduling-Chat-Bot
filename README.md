# UMD course-data scraper and Qdrant sync

This repository scrapes UMD course, section, catalog, course-prefix, and GenEd data, then synchronizes it to Qdrant for the UMD Scheduling Chatbot.

The public chatbot UI lives in [UMD-Scheduling-Chatbot-2.0](https://github.com/aluthra23/UMD-Scheduling-Chatbot-2.0).

## What it stores

Qdrant uses one collection per UMD term ID:

- `YYYY01` — spring term
- `YYYY08` — fall term

For example, `202608` represents Fall 2026. Each collection includes schedule sections (including open and closed sections), catalog data, course prefixes, and GenEd definitions. Vectors use FP32 `sentence-transformers/all-MiniLM-L6-v2` embeddings with 384 dimensions.

## Hourly GitHub Actions workflow

The workflow at `.github/workflows/upload-next-term.yml` runs at minute `00` of every hour, in UTC. It needs these repository Actions secrets:

- `QDRANT_API_KEY`
- `QDRANT_LINK`

On every run it:

1. Finds the newest numeric term collection in Qdrant.
2. Checks whether the next UMD term is published using CMSC351.
3. If it is published, scrapes and creates/synchronizes that new term.
4. Otherwise, scrapes and refreshes the newest available term to capture seat, waitlist, and section changes.

The workflow treats the expected `404 {"detail":"Course not found!"}` response as “not published.” Other API/network failures fail the run instead of silently refreshing the wrong term.

Use the repository’s **Actions** tab and **Run workflow** to launch it manually. Leave the optional term blank for normal automatic behavior, or enter a term ID to force a refresh of that collection.

## Incremental updates

Documents have deterministic UUIDs and content hashes. After a scrape, the uploader:

- embeds and upserts only new or changed documents;
- leaves unchanged Qdrant points intact;
- deletes only documents absent from the new scrape.

This avoids the previous delete-and-reupload outage during normal hourly refreshes. A collection created before incremental metadata existed is rebuilt once on its first refresh; subsequent runs are incremental.

## Local setup

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Set these environment variables in `.env` (or point `ENV_FILE` to a file containing them):

```env
QDRANT_API_KEY=...
QDRANT_LINK=https://...
```

Run a complete scrape and sync for a specific term:

```bash
ENV_FILE=.env .venv/bin/python scripts/scrape_and_upload.py 202608
```

Pass `--recreate` only when a full rebuild is intentionally required:

```bash
ENV_FILE=.env .venv/bin/python scripts/scrape_and_upload.py 202608 --recreate
```

## Important files

- `scripts/scrape_and_upload.py` — runs all scrapers, then uploads one term.
- `scripts/next_term.py` — discovers current and next term IDs from Qdrant.
- `scripts/check_term.py` — checks next-term publication status.
- `main.py` — creates document IDs/hashes and performs incremental sync.
- `qdrant_manager.py` — Qdrant operations and FastEmbed embedding.
- `schedule_of_classes_scraper/` — Testudo section scraper.

## Notes for maintainers

Do not change the embedding model or precision without rebuilding every Qdrant collection and updating the UI query embeddings to match. The UI repository’s deployment environment needs the same Qdrant endpoint/key plus its Gemini API key; never commit credentials.
