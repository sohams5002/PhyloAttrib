"""PhyloAttrib registry metadata crawler (work in progress).

Fetches package metadata from public registry APIs and normalises it into
one schema so packages from different registries can be compared later in
the pipeline.

Currently supported: PyPI, npm. Planned: crates.io, RubyGems.
"""

import argparse
import json
import os
import sys

import requests

PYPI_URL = "https://pypi.org/pypi/{name}/json"
NPM_URL = "https://registry.npmjs.org/{name}"


def fetch_pypi(name: str) -> dict:
    resp = requests.get(PYPI_URL.format(name=name), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    info = data.get("info", {})
    releases = data.get("releases", {})
    return {
        "registry": "pypi",
        "name": info.get("name", name),
        "author": info.get("author") or info.get("maintainer"),
        "author_email": info.get("author_email") or info.get("maintainer_email"),
        "latest_version": info.get("version"),
        "summary": info.get("summary"),
        "requires_dist": info.get("requires_dist") or [],
        "release_count": len(releases),
        "release_times": {
            version: files[0].get("upload_time")
            for version, files in releases.items()
            if files
        },
    }


def fetch_npm(name: str) -> dict:
    resp = requests.get(NPM_URL.format(name=name), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    versions = data.get("versions", {})
    latest_tag = (data.get("dist-tags") or {}).get("latest")
    latest = versions.get(latest_tag, {}) if latest_tag else {}
    author = latest.get("author") or data.get("author") or {}
    return {
        "registry": "npm",
        "name": data.get("name", name),
        "author": author.get("name") if isinstance(author, dict) else author,
        "author_email": author.get("email") if isinstance(author, dict) else None,
        "latest_version": latest_tag,
        "summary": data.get("description"),
        "requires_dist": list((latest.get("dependencies") or {}).keys()),
        "release_count": len(versions),
        "release_times": {
            version: data.get("time", {}).get(version) for version in versions
        },
    }


FETCHERS = {"pypi": fetch_pypi, "npm": fetch_npm}


def main() -> int:
    parser = argparse.ArgumentParser(description="PhyloAttrib metadata crawler")
    parser.add_argument("package", help="package name to fetch")
    parser.add_argument(
        "--registry",
        choices=sorted(FETCHERS),
        default="pypi",
        help="registry to query (default: pypi)",
    )
    parser.add_argument("--out-dir", default="out", help="output directory")
    args = parser.parse_args()

    record = FETCHERS[args.registry](args.package)
    os.makedirs(args.out_dir, exist_ok=True)
    path = os.path.join(args.out_dir, f"{args.registry}-{args.package.replace('/', '_')}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True)
    print(f"wrote {path} ({record['release_count']} releases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
