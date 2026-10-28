MAX_STALE_FRACTION = 0.25
MIN_STALE_TO_GUARD = 20

SCHEDULE_FLAG_COLUMNS = {
    "HAS LECTURE", "HAS 2ND LISTED LECTURE", "HAS 3RD LISTED LECTURE",
    "HAS DISCUSSION", "HAS 2ND LISTED DISCUSSION", "HAS LAB", "HAS 2ND LISTED LAB",
    "IS NORMAL", "IS BLENDED (NORMAL AND ONLINE)", "IS ONLINE",
}


def document_key(source, row):
    if source == "schedule":
        identity = f"{row.get('COURSE NUMBER')}:{row.get('SECTION ID')}"
    elif source == "catalog":
        identity = row.get("COURSE NUMBER")
    elif source == "prefix":
        identity = row.get("COURSE PREFIX")
    else:
        identity = row.get("GENERAL EDUCATION ACRONYM")
    return f"{source}:{str(identity).upper()}"


def delivery_mode(row):
    if row.get("IS BLENDED (NORMAL AND ONLINE)") == "1":
        return "Blended"
    if row.get("IS ONLINE") == "1":
        return "Online"
    if row.get("IS NORMAL") == "1":
        return "Face-to-face"
    return None


def document_text(source, row, columns):
    """Embeddable text for one CSV row (all values are strings).

    Schedule rows replace their 0/1 flag columns with a single DELIVERY field, which keeps far more
    of each section inside the embedding model's 256-token window.
    """
    parts = []
    for column in columns:
        if source == "schedule" and column in SCHEDULE_FLAG_COLUMNS:
            continue
        value = " ".join(str(row.get(column) or "").split())
        if value:
            parts.append(f"{column}: {value}")
        if source == "schedule" and column == "INSTRUCTOR":
            mode = delivery_mode(row)
            if mode:
                parts.append(f"DELIVERY: {mode}")
    return " ".join(parts)


def stale_document_ids(existing, documents, sources, allow_mass_delete=False):
    """Return ids of Qdrant documents (from the given sources) missing from the fresh scrape.

    Raises if a source lost an implausible share of its documents, which almost always means
    the scrape failed rather than that the data really disappeared.
    """
    stale_ids = []
    for source in sources:
        prefix = f"{source}:"
        old_keys = [key for key in existing if key.startswith(prefix)]
        stale_keys = [key for key in old_keys if key not in documents]
        fresh_count = sum(1 for key in documents if key.startswith(prefix))

        scrape_looks_broken = (
            (old_keys and fresh_count == 0)
            or (len(stale_keys) >= MIN_STALE_TO_GUARD and len(stale_keys) > MAX_STALE_FRACTION * len(old_keys))
        )
        if scrape_looks_broken and not allow_mass_delete:
            raise RuntimeError(
                f"Refusing to delete {len(stale_keys)} of {len(old_keys)} '{source}' documents "
                f"({fresh_count} scraped); the scrape probably failed. "
                "Re-run with --allow-mass-delete if this is intended."
            )
        stale_ids.extend(existing[key]["id"] for key in stale_keys)
    return stale_ids
