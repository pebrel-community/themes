"""Offline metadata checks. Actual ZIP contents are checked by the installer."""

import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"id", "name", "version", "author", "source", "license", "archive",
            "unpacked_bytes", "video_bytes"}
OPTIONAL = {"description", "preview", "tags"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, field, limit=256):
    require(isinstance(value, str) and bool(value.strip()), f"{field}: nonempty text required")
    require(len(value.encode("utf-8")) <= limit, f"{field}: text too long")
    require(not any(ord(char) < 32 or ord(char) == 127 for char in value),
            f"{field}: control characters are not accepted")
    return value


def count(value, field, maximum, minimum=0):
    require(type(value) is int and minimum <= value <= maximum,
            f"{field}: expected integer in [{minimum}, {maximum}]")


def https_url(value, field):
    text(value, field, 2048)
    parsed = urlsplit(value)
    require(parsed.scheme == "https" and bool(parsed.hostname)
            and parsed.username is None and parsed.password is None,
            f"{field}: HTTPS URL without credentials required")
    return parsed


def validate(catalog, policy):
    require(isinstance(catalog, dict) and set(catalog) == {"schema_version", "themes"},
            "catalog: expected schema_version and themes")
    require(type(catalog["schema_version"]) is int and catalog["schema_version"] == 1,
            "catalog: unsupported schema_version")
    require(policy.get("schema_version") == 1, "policy: unsupported schema_version")
    limits = ["max_catalog_bytes", "max_entries", "max_video_bytes",
              "max_total_video_bytes", "max_archive_bytes", "max_unpacked_bytes"]
    for key in limits:
        require(type(policy.get(key)) is int and policy[key] > 0,
                f"policy: positive {key} required")
    require(policy["max_video_bytes"] <= policy["max_total_video_bytes"]
            <= policy["max_unpacked_bytes"], "policy: inconsistent video limits")
    entries = catalog["themes"]
    require(isinstance(entries, list) and len(entries) <= policy["max_entries"],
            "catalog: invalid or oversized themes list")
    ids = set()
    for entry in entries:
        require(isinstance(entry, dict) and REQUIRED <= set(entry)
                <= REQUIRED | OPTIONAL, "theme: missing or unknown fields")
        identifier = text(entry["id"], "id", 128)
        require(re.fullmatch(r"[a-z0-9][a-z0-9-]*/[a-z0-9][a-z0-9-]*", identifier),
                "id: use lowercase author/theme-name")
        require(identifier not in ids, f"id: duplicate {identifier}")
        ids.add(identifier)
        text(entry["name"], "name", 128)
        version = text(entry["version"], "version", 64)
        require(re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?", version),
                "version: use major.minor.patch with optional prerelease")
        author = entry["author"]
        require(isinstance(author, dict) and set(author) == {"name", "github"},
                "author: expected name and github")
        text(author["name"], "author.name", 128)
        handle = text(author["github"], "author.github", 39)
        require(re.fullmatch(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", handle),
                "author.github: invalid GitHub handle")
        source = https_url(entry["source"], "source")
        require(source.netloc == "github.com" and not source.query and not source.fragment
                and re.fullmatch(r"/[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", source.path),
                "source: expected a GitHub repository URL")
        text(entry["license"], "license", 128)
        archive = entry["archive"]
        require(isinstance(archive, dict) and set(archive) == {"url", "sha256", "bytes"},
                "archive: expected url, sha256, and bytes")
        release = https_url(archive["url"], "archive.url")
        prefix = source.path + "/releases/download/"
        require(release.netloc == "github.com" and not release.query and not release.fragment
                and release.path.startswith(prefix),
                "archive.url: use a release in the declared source repository")
        parts = release.path[len(prefix):].split("/")
        require(len(parts) == 2 and parts[0] and parts[0].lower() != "latest"
                and parts[1].endswith(".pebrel-theme.zip"),
                "archive.url: versioned .pebrel-theme.zip release required")
        require(isinstance(archive["sha256"], str)
                and re.fullmatch(r"[0-9a-f]{64}", archive["sha256"]),
                "archive.sha256: lowercase SHA-256 required")
        count(archive["bytes"], "archive.bytes", policy["max_archive_bytes"], 1)
        count(entry["unpacked_bytes"], "unpacked_bytes", policy["max_unpacked_bytes"], 1)
        count(entry["video_bytes"], "video_bytes", policy["max_total_video_bytes"])
        require(entry["video_bytes"] <= entry["unpacked_bytes"],
                "video_bytes: cannot exceed unpacked_bytes")
        if "description" in entry:
            text(entry["description"], "description", 1024)
        if "preview" in entry:
            https_url(entry["preview"], "preview")
        if "tags" in entry:
            tags = entry["tags"]
            require(isinstance(tags, list) and len(tags) <= 12, "tags: at most 12 tags")
            for tag in tags:
                text(tag, "tag", 32)
            require(len(set(tags)) == len(tags), "tags: duplicates are not accepted")
    return len(entries)


def main():
    policy_path = ROOT / "policy.json"
    require(policy_path.stat().st_size <= 4096, "policy: file too large")
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    count(policy.get("max_catalog_bytes"), "max_catalog_bytes", 1024 * 1024, 1)
    catalog_path = ROOT / "catalog/index.json"
    with catalog_path.open("rb") as stream:
        payload = stream.read(policy["max_catalog_bytes"] + 1)
    require(len(payload) <= policy["max_catalog_bytes"], "catalog: file too large")
    catalog = json.loads(payload)
    total = validate(catalog, policy)
    print(f"Catalog metadata valid: {total} themes; downloads and playback not tested.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, OSError, KeyError) as error:
        print(f"Catalog check failed: {error}", file=sys.stderr)
        sys.exit(1)
