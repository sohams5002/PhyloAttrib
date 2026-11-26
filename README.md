# PhyloAttrib

> **Status: work in progress - early development, design may change.**

PhyloAttrib is a malware lineage attribution engine. It traces related malware campaigns across public package registries by collecting package metadata and code, then analysing similarity between packages to cluster releases that likely share an author or campaign.

Supply-chain malware rarely appears once. The same actor republishes variants across npm, PyPI, crates.io and RubyGems, often renamed. PhyloAttrib aims to surface those links.

## How it works (design)

1. **Collect** - crawl package metadata (names, versions, authors, publish times, dependencies) from the registries' public APIs. See `crawler.py` for the current metadata collector (PyPI + npm so far).
2. **Clean** - normalise author handles, timestamps and dependency lists into one schema so registries can be compared like-for-like.
3. **Compare** - score code similarity between packages. Planned: AST-based similarity with tree-sitter so simple renames and reformatting don't fool it.
4. **Attribute** - build a lineage graph with NetworkX (packages as nodes, similarity + timing edges) and cluster it into candidate campaigns.

## Roadmap

- [x] Registry metadata crawler (PyPI JSON API, npm registry API)
- [ ] crates.io and RubyGems collectors
- [ ] Normalised storage schema
- [ ] tree-sitter based code-similarity scoring
- [ ] NetworkX lineage graph + clustering
- [ ] CLI and report output

## Run the crawler

```
pip install -r requirements.txt
python crawler.py requests --registry pypi
python crawler.py express --registry npm
```

Metadata is written to `out/<registry>-<package>.json`.

## Stack

Python, NetworkX, tree-sitter (planned), scikit-learn (planned)
