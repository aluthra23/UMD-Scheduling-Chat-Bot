import unittest

from sync_utils import stale_document_ids


def existing_docs(source, count):
    return {f"{source}:{index}": {"id": f"{source}-id-{index}"} for index in range(count)}


def fresh_docs(source, indices):
    return {f"{source}:{index}": {} for index in indices}


class StaleDocumentIdsTests(unittest.TestCase):
    def test_returns_only_missing_documents(self):
        existing = existing_docs("schedule", 100)
        documents = fresh_docs("schedule", range(95))
        stale = stale_document_ids(existing, documents, {"schedule"})
        self.assertEqual(sorted(stale), sorted(f"schedule-id-{index}" for index in range(95, 100)))

    def test_ignores_sources_that_were_not_scraped(self):
        existing = {**existing_docs("schedule", 100), **existing_docs("gen_ed", 30)}
        documents = fresh_docs("gen_ed", range(30))
        self.assertEqual(stale_document_ids(existing, documents, {"gen_ed"}), [])

    def test_refuses_when_a_source_scraped_nothing(self):
        existing = existing_docs("gen_ed", 30)
        with self.assertRaisesRegex(RuntimeError, "gen_ed"):
            stale_document_ids(existing, {}, {"gen_ed"})

    def test_refuses_when_most_of_a_source_disappears(self):
        existing = existing_docs("schedule", 1000)
        documents = fresh_docs("schedule", range(600))
        with self.assertRaisesRegex(RuntimeError, "400 of 1000"):
            stale_document_ids(existing, documents, {"schedule"})

    def test_small_source_with_few_stale_documents_is_allowed(self):
        existing = existing_docs("gen_ed", 30)
        documents = fresh_docs("gen_ed", range(20))
        self.assertEqual(len(stale_document_ids(existing, documents, {"gen_ed"})), 10)

    def test_override_allows_mass_delete(self):
        existing = existing_docs("schedule", 1000)
        stale = stale_document_ids(existing, {}, {"schedule"}, allow_mass_delete=True)
        self.assertEqual(len(stale), 1000)

    def test_empty_collection_has_nothing_stale(self):
        self.assertEqual(stale_document_ids({}, fresh_docs("schedule", range(5)), {"schedule"}), [])


if __name__ == "__main__":
    unittest.main()
