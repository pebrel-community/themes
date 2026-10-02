import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_catalog", ROOT / "scripts/check_catalog.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)
POLICY = json.loads((ROOT / "policy.json").read_text(encoding="utf-8"))


def example():
    return {
        "id": "creator/quiet-night", "name": "安静的夜晚", "version": "1.0.0",
        "author": {"name": "Example author", "github": "creator"},
        "source": "https://github.com/creator/quiet-night", "license": "CC-BY-4.0",
        "archive": {
            "url": "https://github.com/creator/quiet-night/releases/download/v1.0.0/night.pebrel-theme.zip",
            "sha256": "a" * 64, "bytes": 1024,
        },
        "unpacked_bytes": 2048, "video_bytes": 0,
        "tags": ["dark", "静态背景"],
    }


class CatalogTests(unittest.TestCase):
    def validate(self, entries):
        return CHECK.validate({"schema_version": 1, "themes": entries}, POLICY)

    def test_real_catalog_starts_empty(self):
        catalog = json.loads((ROOT / "catalog/index.json").read_text(encoding="utf-8"))
        self.assertEqual(CHECK.validate(catalog, POLICY), 0)

    def test_unicode_author_and_theme_are_accepted(self):
        entry = example()
        entry["author"]["name"] = "社区作者"
        self.assertEqual(self.validate([entry]), 1)

    def test_org_source_and_different_author_are_accepted(self):
        entry = example()
        entry["source"] = "https://github.com/art-collective/night"
        entry["archive"]["url"] = "https://github.com/art-collective/night/releases/download/v1.0.0/night.pebrel-theme.zip"
        self.assertEqual(self.validate([entry]), 1)

    def test_size_boundaries_are_inclusive(self):
        entry = example()
        entry["archive"]["bytes"] = POLICY["max_archive_bytes"]
        entry["unpacked_bytes"] = POLICY["max_unpacked_bytes"]
        entry["video_bytes"] = POLICY["max_total_video_bytes"]
        self.assertEqual(self.validate([entry]), 1)

    def test_each_size_limit_rejects_one_byte_over(self):
        for field, key in [("video_bytes", "max_total_video_bytes"),
                           ("unpacked_bytes", "max_unpacked_bytes"),
                           ("archive.bytes", "max_archive_bytes")]:
            with self.subTest(field=field):
                entry = example()
                if field == "archive.bytes":
                    entry["archive"]["bytes"] = POLICY[key] + 1
                else:
                    entry[field] = POLICY[key] + 1
                with self.assertRaises(ValueError):
                    self.validate([entry])

    def test_boolean_size_and_video_accounting_are_rejected(self):
        for field, value in [("video_bytes", True), ("video_bytes", 2049)]:
            entry = example()
            entry[field] = value
            with self.assertRaises(ValueError):
                self.validate([entry])

    def test_mutable_or_unrelated_downloads_are_rejected(self):
        for url in [
            "https://github.com/creator/quiet-night/releases/latest/download/night.pebrel-theme.zip",
            "https://github.com/creator/quiet-night/releases/download/latest/night.pebrel-theme.zip",
            "https://github.com/other/project/releases/download/v1.0.0/night.pebrel-theme.zip",
            "https://github.com@evil.example/creator/quiet-night/releases/download/v1.0.0/night.pebrel-theme.zip",
        ]:
            with self.subTest(url=url):
                entry = example()
                entry["archive"]["url"] = url
                with self.assertRaises(ValueError):
                    self.validate([entry])

    def test_duplicates_unknown_fields_and_invalid_hashes_are_rejected(self):
        original = example()
        with self.assertRaises(ValueError):
            self.validate([original, copy.deepcopy(original)])
        for key, value in [("archive", {**original["archive"], "sha256": "invalid"}),
                           ("unknown", "value"), ("tags", ["dark", "dark"])]:
            entry = example()
            entry[key] = value
            with self.assertRaises(ValueError):
                self.validate([entry])


if __name__ == "__main__":
    unittest.main()
