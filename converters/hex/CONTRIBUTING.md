<!--
  Licensed to the Apache Software Foundation (ASF) under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  The ASF licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing,
  software distributed under the License is distributed on an
  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
  KIND, either express or implied.  See the License for the
  specific language governing permissions and limitations
  under the License.
-->

# Contributing to the Ossie–Hex converter

This document covers development of the `ossie-hex` package. Repository-wide
contribution, review, and Apache release requirements are documented in the
[project contribution guide][ossie-contributing].

## Prerequisites

- Python 3.11 or newer
- [uv]
- A checkout of the complete Apache Ossie repository

```bash
cd converters/hex
uv sync
```

## Development

TODO(development): {workflow-description}

### Python

TODO(development): {python-description}

### CLI

TODO(development): {cli-description}

## Verification

Run the following commands to verify your changes.

```bash
# lint and formatting checks
uv run poe check

# apply automatic fixes for lint and formatting issues
uv run poe format

# run complete test suite
uv run poe test

# run a single file or test
uv run poe test tests/<file>.py
uv run poe test tests/<file>.py::<test>
```

### Snapshots

Full Hex/Ossie translations use [syrupy] and live under `tests/__snapshots__/`.
Smaller structured expectations use [inline-snapshot] and are stored beside the
assertion in the test source.

When converter output changes intentionally, regenerate Syrupy snapshots:

```bash
# Regenerate large snapshots
uv run pytest --snapshot-update

# Interactively update small snapshots
uv run pytest --inline-snapshot=review

# Apply fixes non-interactively
uv run pytest --inline-snapshot=fix
```

Inspect the resulting diffs before committing. Do not pass snapshot-update flags
in CI; a normal `uv run pytest` must fail when snapshots drift.

### CI/CD

CI runs installation, linting, formatting, and testing on Python 3.11 through
3.14 using `.github/workflows/converter-hex-ci.yml`.

To reproduce the CI Python version matrix locally, first install the supported
interpreters with a current `uv` release, then run each test suite in an
isolated environment:

```bash
uv python install 3.11 3.12 3.13 3.14

for python_version in 3.11 3.12 3.13 3.14; do
  uv run --isolated --python "${python_version}" pytest || exit 1
done
```

The isolated environments leave the project's `.venv` unchanged. Keep `uv`
up to date so version selectors resolve to stable Python releases rather than
an older prerelease installation.

## Building distributions

Build the source distribution and wheel from this directory:

```bash
uv build
```

The artifacts are written to `dist/`. Before publishing, inspect their metadata
and contents:

```bash
uvx twine check dist/*
uv run python -m zipfile -l dist/*.whl
tar -tf dist/*.tar.gz
```

Also test installation in a clean environment. This will only work from PyPI
after the `apache-ossie` dependency has been published:

```bash
uv venv /tmp/ossie-hex-release-test
uv pip install --python /tmp/ossie-hex-release-test/bin/python dist/*.whl
/tmp/ossie-hex-release-test/bin/ossie-hex --help
```

## Publishing

Publishing is deferred to the Apache Ossie project, which governs the broader
release cycle. Contributors should not publish this package independently.

[ossie-contributing]: ../../CONTRIBUTING.md

[uv]: https://docs.astral.sh/uv/
[syrupy]: https://github.com/syrupy-project/syrupy
[inline-snapshot]: https://15r10nk.github.io/inline-snapshot/
