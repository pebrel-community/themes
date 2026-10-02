# Community theme directory bootstrap

## Status

Metadata directory implemented and published; application integration is pending.

## Context

The community needs a dedicated place to share work and attribution without
putting every theme or large media file into the desktop application's binary.
Windows, macOS, and Linux support, low memory use, and bounded media size are
required for the future installer and renderer.

## Evidence

The application already has versioned theme JSON, a local theme library, and
static background image rendering. This directory does not implement a ZIP
installer, video decoder, animation scheduler, or GPU shader execution.
The initial catalog and its tests contain no published sample work.

## Decision

Keep author source and assets in their repositories and versioned releases.
Maintain an empty, versioned metadata catalog and source/author/license rules.
Use `policy.json` as the shared byte-limit authority for offline directory checks.
Actual installation must recheck stream sizes, archive contents, and integrity.
Catalog versioning is independent of theme document and ZIP manifest versioning.

## Rejected alternatives

- Commit theme ZIPs and videos into Git: makes repository history accumulate assets.
- Fill the catalog with example works: misrepresents authorship and availability.
- Treat declared sizes or a successful metadata check as package verification:
  downloaded bytes still need independent validation.
- Add decoding and shader dependencies to this repository: runtime ownership
  belongs to the application.

## Consequences

Authors can prepare submissions without organization membership. Directory
metadata is useful for later discovery, but playback compatibility remains
unverified until tested by the application. A workflow is not server-side
branch protection.

## Validation

The offline validator and all eight positive/negative tests passed with
standard-library Python. Initial hosted catalog validation also passed in
[run 36978107487](https://github.com/pebrel-community/themes/actions/runs/36978107487).
This is metadata validation, not installer, decoding, or playback validation.

## Supersedes

None.

## Revisit when

The application ZIP installer defines its manifest or the first real community
theme requires a metadata change; version the directory contract when necessary.
