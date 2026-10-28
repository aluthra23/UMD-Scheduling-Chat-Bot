# UMD course-data scraper and Qdrant sync

This repository scrapes UMD course sections, catalog entries, course prefixes, and gen-ed categories, then syncs them into Qdrant for the UMD Scheduling Chatbot.

It is one of three related repositories:

| Repository | Role |
| --- | --- |
| **UMD-Scheduling-Chat-Bot** (this one) | Scrapes UMD's websites and keeps the Qdrant collections up to date. |
| [UMD-Scheduling-Chatbot-2.0](https://github.com/aluthra23/UMD-Scheduling-Chatbot-2.0) | The Next.js chat app, hosted at <https://umd-chatbot.vercel.app/>. It reads the collections this repository writes. |
| [UMD-Courses-API](https://github.com/aluthra23/UMD-Courses-API) | A public FastAPI service that scrapes UMD on demand. This pipeline uses it to detect newly published terms. |

`app.py` is a leftover Streamlit page that only points visitors to the new chat app.

## What it stores

Qdrant has one collection per UMD term ID:

- `YYYY01`: spring term
- `YYYY08`: fall term

For example, `202701` is Spring 2027. Each collection holds four kinds of documents, recorded in the `source` payload field:

| `source` | One document per | Scraped from |
| --- | --- | --- |
| `schedule` | Undergraduate section (open and closed) | Testudo Schedule of Classes |
| `catalog` | Undergraduate catalog course | UMD Academic Catalog |
| `prefix` | Course prefix, such as `CMSC` | Testudo and the catalog |
| `gen_ed` | Gen-ed category | Testudo |

Each document's payload has `text`, `source`, `course_number` (indexed, so the chat app can filter by course), `document_key`, and `content_hash`. Schedule documents leave out the per-section `HAS …` / `IS …` 0/1 columns and use a single `DELIVERY:` field (`Face-to-face`, `Blended` or `Online`) instead. That keeps most sections inside the embedding model's 256-token limit.

Vectors are FP32 `sentence-transformers/all-MiniLM-L6-v2` embeddings with 384 dimensions, made with FastEmbed. The chat app embeds questions with the same model in the browser. Both sides produce identical vectors, so never change the model on only one side.

A separate `sync_status` collection holds one point per term, with the time of its last successful sync (`synced_at`) and document counts. The chat app shows that time to students.

## GitHub Actions workflow

`.github/workflows/upload-next-term.yml` is scheduled for minute `17` of every hour (UTC). GitHub throttles scheduled workflows, so in practice it runs every few hours. It needs these repository Actions secrets:

- `QDRANT_API_KEY`
- `QDRANT_LINK`

On every run it:

1. Finds the newest term collection in Qdrant (`scripts/next_term.py`).
2. Asks the UMD Courses API whether the following term is published, by requesting CMSC351 sections for it (`scripts/check_term.py`). A `404 {"detail": "Course not found!"}` means "not published yet". The script retries timeouts and server errors, since the API runs on Koyeb's free tier and can be slow to wake up.
3. If the next term is published, scrapes it and creates its collection.
4. Otherwise, scrapes and refreshes the newest term to pick up seat, waitlist, and section changes.

Only the newest term is refreshed. Older term collections stay as they were when the next term appeared.

To run it manually, open the repository's **Actions** tab and choose **Run workflow**. Leave the term blank for the normal behaviour, or enter a term ID to refresh that collection.

The embedding model is cached between runs in `.cache/fastembed`, via `FASTEMBED_CACHE_PATH`.

## Incremental sync and safety checks

Documents have deterministic UUIDs and content hashes. After each scrape, `main.py`:

- embeds and upserts only new or changed documents, leaving unchanged points alone;
- deletes documents that are missing from the new scrape;
- records the sync time in `sync_status`.

Several safeguards stop a bad scrape from wiping data:

- Every request to UMD's websites goes through `helping_files/http_utils.fetch`. It retries timeouts, connection errors, 429s, and 5xx responses, and raises once retries run out. A failed page is never mistaken for an empty one.
- Before deleting anything, `main.py` refuses to remove more than 25% of a source's documents (or all of them) unless you pass `--allow-mass-delete`.
- The gen-ed scraper only rewrites `gen_eds.csv` after a successful scrape, and fails if it finds no categories.
- CSVs are read as text, so IDs like section `0101` are never turned into numbers.

A collection created before incremental metadata existed is rebuilt once on its first sync. Pass `--recreate` to force a rebuild.

## Local setup

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Put the Qdrant credentials in `.env` (or point `ENV_FILE` at another file):

```env
QDRANT_API_KEY=...
QDRANT_LINK=https://...
```

Scrape and sync one term:

```bash
.venv/bin/python scripts/scrape_and_upload.py 202701
```

Only pass `--recreate` when a full rebuild is intentional:

```bash
.venv/bin/python scripts/scrape_and_upload.py 202701 --recreate
```

To test changes without touching a real term, sync into a throwaway collection, then delete it:

```bash
.venv/bin/python main.py --collection zz-test
```

## Tests

```bash
PYTHONPATH=.:scripts .venv/bin/python -m unittest discover -s tests
```

The tests cover the retrying fetch, the deletion guard, term-date logic, document keys and text, the term check, and scraper edge cases.

## Important files

- `scripts/scrape_and_upload.py`: runs every scraper, then syncs one term.
- `scripts/next_term.py`: finds the newest uploaded term and the term after it.
- `scripts/check_term.py`: asks the UMD Courses API whether a term is published.
- `main.py`: builds documents and runs the incremental sync.
- `sync_utils.py`: document keys and text, and the deletion guard.
- `qdrant_manager.py`: Qdrant operations, FastEmbed embedding, and the sync-status record.
- `schedule_of_classes_scraper/`, `course_catalog_scraper/`, `course_prefixes_dataset_creation/`, `gen_eds/`: the scrapers.

## Code shared with UMD-Courses-API

Both repositories scrape the same UMD pages. These files are identical in both and should be changed together:

- `helping_files/helper.py`
- `helping_files/http_utils.py`
- `course_prefixes_dataset_creation/course_prefixes_scraper.py`

The Schedule of Classes scrapers parse Testudo the same way but produce different output: CSV rows here, API response models there. Their parsing fixes are applied to both by hand. They intentionally differ in scope. This pipeline scrapes undergraduate sections and the undergraduate catalog. The API also covers graduate courses.

## Notes for maintainers

Do not change the embedding model, precision, or document format without re-syncing every collection the chat app uses. The chat app's deployment needs the same Qdrant endpoint and key, plus its Gemini API key. Never commit credentials.
