#!/usr/bin/env python3
"""Run the form repository's bilingual gate against a chosen hub dictionary.

tools/i18n-check.py reads the shared dictionary from a sibling `hub/`
directory, which on this host is an untracked staging copy. This wrapper
points it at the real, tracked dictionary in the hub worktree instead, so
the gate is run against the artifact that would actually be released.

  python3 tools/i18n-check-against-hub.py ../hub-translation/assets/i18n-strings.js
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECK = HERE / "i18n-check.py"


def load():
    spec = importlib.util.spec_from_file_location("i18n_check", CHECK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    dictionary = str(Path(sys.argv[1]).resolve())
    if not Path(dictionary).is_file():
        print(f"no dictionary at {dictionary}")
        return 2
    module = load()
    module.STRINGS = dictionary
    print(f"dictionary under test: {dictionary}")
    return module.main([])


if __name__ == "__main__":
    sys.exit(main())
