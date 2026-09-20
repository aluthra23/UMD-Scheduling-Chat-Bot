MAX_STALE_FRACTION = 0.25
MIN_STALE_TO_GUARD = 20


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
