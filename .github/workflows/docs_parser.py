#!/usr/bin/env python3
"""
CI script for making a Wiki files for Universal Pipeline Wrapper by Alexander Bazhenov.

This Source Code Form is subject to the terms of the MIT License. If a copy of the
source was not distributed with this file, You can obtain one at:
https://github.com/alexanderbazhenoff/universal-wrapper-pipeline-settings/blob/main/LICENSE
"""
import locale
import os
import re


def load_and_replace_md_file(file_path, regex="", replacement=""):
    """Read markdown file and replace by regex."""
    with open(file_path, "r", encoding=locale.getpreferredencoding()) as file:
        return re.sub(regex, replacement, file.read(), flags=re.DOTALL)


JENKINS_SRC = "jenkins_src"
SETTINGS_URL = (
    "https://github.com/alexanderbazhenoff/"
    "universal-wrapper-pipeline-settings/blob/main/settings/"
)
SETTINGS_REGEX = "\\]\\(settings/"
WIKI_FILES = ["Home.md", "Settings file format.md"]
WIKI_PATH_PREFIX = "wiki_"
LANG = os.environ.get("CI_WIKI_LANG", "eng")
README_POSTFIX = "_RUS" if LANG == "rus" else ""
REGEX_PREFIX = "<!-- docs-ci-cut-"
FORMAT_README = f"README{README_POSTFIX}.md"
HOME_README = f"{JENKINS_SRC}/{FORMAT_README}"
CUT_REGEX = f"\n{REGEX_PREFIX}begin -->(.*?){REGEX_PREFIX}end -->\n"

home_head = load_and_replace_md_file(f".github/workflows/wiki_head_{LANG}.md")
wiki_items = [f"{home_head}{load_and_replace_md_file(HOME_README, CUT_REGEX)}"]
conf_md_raw = load_and_replace_md_file(FORMAT_README, CUT_REGEX)
wiki_items.append(re.sub(SETTINGS_REGEX, f"]({SETTINGS_URL}", conf_md_raw))

for idx, x in enumerate(wiki_items):
    with open(
        f"{WIKI_PATH_PREFIX}{LANG}/{WIKI_FILES[idx]}",
        "w",
        encoding=locale.getpreferredencoding(),
    ) as f:
        f.write(x)
        f.close()
