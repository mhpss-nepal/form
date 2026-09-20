#!/usr/bin/env python3
"""Extract the English for every i18n key now used by the three keyed forms.

Run from the form repository root. Writes tools/new-i18n-entries.json, a
list of {"key","en","html"} for every key the pages use, so the dictionary
can be built from the pages themselves rather than retyped.
"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["referral.html", "phq9.html", "contact.html"]
KEY_ATTRS = ["data-i18n", "data-i18n-ph", "data-i18n-aria", "data-i18n-alt", "data-i18n-title"]
VOID = {"meta", "link", "input", "br", "hr", "img", "source", "area"}


class Node:
    def __init__(self, tag, attrs, end_start):
        self.tag = tag
        self.attrs = dict(attrs)
        self.end_start = end_start
        self.end = None
        self.parent = None
        self.text = []


class Parser(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.nodes = []
        self.stack = []
        self.lines = [0]
        for match in re.finditer("\n", source):
            self.lines.append(match.end())

    def position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        end_start = self.source.find(">", self.position()) + 1
        node = Node(tag, attrs, end_start)
        self.nodes.append(node)
        if self.stack:
            node.parent = self.stack[-1]
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1].tag == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].tag == tag:
                self.stack[index].end = self.position()
                self.stack = self.stack[:index]
                break

    def handle_data(self, data):
        if self.stack:
            self.stack[-1].text.append(data)


def tidy(value):
    return re.sub(r"\s+", " ", value).strip()


def js_unescape(value):
    """Undo JS string escapes, leaving non-ASCII characters alone.

    The shortcut ``value.encode().decode("unicode_escape")`` decodes the
    UTF-8 bytes as Latin-1, so an em dash comes back as three mojibake
    characters. tools/i18n-check.py carries the same helper and the same
    warning; this text is inserted into a Ministry-facing page, so it is
    not a cosmetic detail.
    """
    out, index = [], 0
    simple = {'"': '"', "\\": "\\", "/": "/", "n": "\n", "t": "\t", "r": "\r",
              "b": "\b", "f": "\f", "'": "'", "`": "`"}
    while index < len(value):
        char = value[index]
        if char != "\\":
            out.append(char)
            index += 1
            continue
        nxt = value[index + 1] if index + 1 < len(value) else ""
        if nxt == "u" and index + 6 <= len(value):
            try:
                out.append(chr(int(value[index + 2:index + 6], 16)))
                index += 6
                continue
            except ValueError:
                pass
        out.append(simple.get(nxt, nxt))
        index += 2
    return "".join(out)


def collect(path):
    source = path.read_text(encoding="utf-8")
    parser = Parser(source)
    parser.feed(source)
    out = {}
    for node in parser.nodes:
        for attr in KEY_ATTRS:
            key = node.attrs.get(attr)
            if not key:
                continue
            if attr == "data-i18n" and node.end is not None:
                if "data-i18n-html" in node.attrs:
                    value = tidy(source[node.end_start:node.end])
                else:
                    direct = "".join(node.text)
                    value = tidy(direct) if tidy(direct) else tidy(source[node.end_start:node.end])
            elif attr == "data-i18n-ph":
                value = node.attrs.get("placeholder", "")
            elif attr == "data-i18n-aria":
                value = node.attrs.get("aria-label", "")
            elif attr == "data-i18n-alt":
                value = node.attrs.get("alt", "")
            else:
                value = node.attrs.get("title", "")
            if not value:
                continue
            if key in out and out[key]["en"] != value:
                raise SystemExit(f"key {key} has two different English values in {path.name}")
            out[key] = {"key": key, "en": value,
                        "html": "data-i18n-html" in node.attrs, "page": path.name}
    return out


def js_keys(path):
    """Keys the page mints in JavaScript rather than in its markup."""
    source = path.read_text(encoding="utf-8")
    found = {}
    if path.name == "phq9.html":
        items = re.search(r"var ITEMS = \[(.*?)\n  \];", source, re.S).group(1)
        for key, text in re.findall(r'key: "([^"]+)", text: "((?:[^"\\]|\\.)*)"', items):
            # Unescape the JS string literal. Do NOT use encode().decode(
            # "unicode_escape"): it reads the UTF-8 bytes as Latin-1 and an
            # em dash comes back as three mojibake characters, which is the
            # exact trap assets/i18n-check.py warns about -- and this text
            # goes into a Ministry-facing page.
            found[key] = {"key": key, "en": js_unescape(text), "html": False, "page": path.name}
        opts = re.search(r"var OPTS = \[(.*?)\n  \];", source, re.S).group(1)
        for key, text in re.findall(r'key: "([^"]+)", l: "((?:[^"\\]|\\.)*)"', opts):
            found[key] = {"key": key, "en": text, "html": False, "page": path.name}
        # the instruction after item 9 is built by concatenating single-quoted
        # JS fragments into innerHTML. Join them the way the browser would and
        # drop the wrapper element the page supplies, so the dictionary entry
        # is exactly the text the reader sees. This string is a safety
        # instruction under a professionalOnly prefix and MUST have a key --
        # without one the engine prints [phq9.item9Instruction] on the page.
        m = re.search(r"\$\(" + '"' + r"risk" + '"' + r"\)\.innerHTML = '(.*?)';", source, re.S)
        if m:
            joined = re.sub(r"'\s*\+\s*'", "", m.group(1)).replace("\\'", "'")
            joined = re.sub(r"^<div[^>]*>", "", joined)
            joined = re.sub(r"</div>\s*$", "", joined)
            found["phq9.item9Instruction"] = {
                "key": "phq9.item9Instruction", "en": tidy(joined),
                "html": True, "page": path.name}
    return found


def main():
    entries = {}
    for page in PAGES:
        path = ROOT / page
        entries.update(collect(path))
        entries.update(js_keys(path))
    ordered = [entries[k] for k in sorted(entries)]
    output = ROOT / "tools" / "new-i18n-entries.json"
    output.write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(ordered)} keys extracted -> {output.relative_to(ROOT)}")
    by_page = {}
    for entry in ordered:
        by_page[entry["page"]] = by_page.get(entry["page"], 0) + 1
    for page, count in sorted(by_page.items()):
        print(f"  {page}: {count}")
    protected = [e["key"] for e in ordered
                 if e["key"].startswith(("phq9.item", "phq9.scale", "phq9.cutoff",
                                         "consent.", "safeguard.", "clinical."))]
    print(f"  protected by professionalOnly: {len(protected)}")
    for key in protected:
        print(f"    {key}")


if __name__ == "__main__":
    main()
