# Pebrel Themes

[中文](README.zh-CN.md)

The theme directory for [Pebrel Community](https://github.com/pebrel-community).
Share your work with author attribution, previews, source, and a versioned ZIP.

**Bootstrap status:** the catalog is empty. The community directory is being
established; ZIP installation, animated backgrounds, and GLSL execution are not
claimed as shipped application features by this repository.

## Share a theme

Publish the ZIP in your own GitHub Release, then submit one entry to
[`catalog/index.json`](catalog/index.json). Keep the assets in your release;
do not commit videos or theme ZIPs to this repository.

Each entry records:

- Stable `id` (`author/theme-name`), `name`, and `version`.
- `author`: display `name` and GitHub `github` handle.
- `source`: the source repository's HTTPS GitHub URL.
- `license`: the theme license; adapted assets need their own attribution.
- `archive`: versioned release `url`, lowercase `sha256`, and actual `bytes`.
- `unpacked_bytes` and `video_bytes`: declared total sizes, checked again by
  the installer against the actual archive when that capability is available.
- Optional `description`, `preview`, and `tags`.

The catalog schema version describes directory metadata, not the version of the
application's theme document or ZIP manifest. The application ZIP manifest will
be versioned separately when its installer contract is implemented.

## Size limits

The authoritative byte limits are in [`policy.json`](policy.json):

| Item | Maximum |
| --- | --- |
| One video | 32 MiB |
| All videos in one theme | 32 MiB |
| Downloaded theme ZIP | 48 MiB |
| All uncompressed files | 64 MiB |

One MiB is 1,048,576 bytes. Splitting a video into multiple files does not
increase the total video allowance. ZIP compression does not reduce the
uncompressed-video allowance. These are sharing limits, not decoded-memory
budgets or guarantees of playback performance.

Short 1080p / 30 FPS loops are the initial authoring recommendation. Runtime
resolution, frame queues, GPU resources, and background shader budgets will be
controlled separately in Pebrel. A video must satisfy both file and runtime
requirements once playback is supported.

## Catalog checks

Python 3.11 or newer, with no third-party Python packages:

```sh
python3 scripts/check_catalog.py
python3 -m unittest discover -s tests
```

The checks are offline and validate metadata, pinned GitHub release links,
identity, and declared size limits. They do not download or decode a work and
must not be reported as successful application installation or playback.

See the [shared contribution guide](https://github.com/pebrel-community/.github/blob/main/CONTRIBUTING.md).

## License

Directory tooling is MIT licensed. Submitted works and previews retain their
own licenses; inclusion does not relicense an author's work.
