# Releasing

Releases are cut from the `release` branch. The `ci.yml` workflow runs full
CI (Tier 1 + Tier 2 against the pinned harfrust corpus) on every push to
`release`. The `release.yml` workflow gates on tag-equals-release-tip, so
the SHA being released has demonstrably passed full CI.

## Guarantees in place

- **Branch protection on `release`** — direct pushes blocked, all commits
  must come through a PR with the `ci` and `release-source-gate` checks
  passing, branch must be up to date with base, no force pushes.
- **`release-source-gate` job (`ci.yml`)** — rejects any PR targeting
  `release` whose head ref isn't `main`. Required check.
- **`gate` job (`release.yml`)** — rejects any tag whose SHA isn't the
  current tip of `release`. Together with the protections above, this
  means tip-of-release = "full CI + Tier 2 passed on this exact SHA."
- **PyPI trusted publishing** — the `publish` job uploads via OIDC, no
  API tokens in GitHub secrets.

## Release procedure

1. Open a PR from `main` to `release`. Wait for CI (including Tier 2) to
   go green. Merge.
2. Tag the tip of `release`:
   ```bash
   git checkout release
   git pull --ff-only
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin vX.Y.Z
   ```
3. The tag push triggers `release.yml`. The `gate` job verifies
   `vX.Y.Z` points to the current tip of `release`. If it doesn't, the
   whole workflow fails — fix and re-tag.
4. Wheel jobs build for Linux (x86_64, aarch64), macOS (x86_64, aarch64),
   Windows (x64) across CPython 3.11/3.12/3.13. The `sdist` job builds
   the source distribution.
5. The `publish` job uploads everything to PyPI via OIDC. `skip-existing`
   makes re-runs idempotent.

## Common issues

**Gate fails: "tag is not the tip of release."** Someone else merged to
`release` between when you fetched and when you pushed the tag, or you
tagged the wrong branch. Delete the tag locally and on origin, pull
`release`, retag.

```bash
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z
git checkout release && git pull --ff-only
git tag -a vX.Y.Z -m "vX.Y.Z" && git push origin vX.Y.Z
```

**Publish fails on PyPI.** Most often the version in `pyproject.toml`
hasn't been bumped (PyPI rejects re-uploads of an existing version).
Bump the version on `main`, merge to `release`, retag.
