#!/usr/bin/env python3
"""Key up referral.html, phq9.html and contact.html.

Run from the form repository root, on a clean checkout of the three pages.
This is text extraction only: it adds data-i18n* attributes and wraps
labelled text in <span> where a control shares the label. It does NOT change
any field id, name, value, validation, storage or submit behaviour, and a
test asserts that (test_i18n_keying.py).

Two rules it applies that a naive sweep gets wrong:

  1. LABEL TEXT NEXT TO A CONTROL. <label><input type="radio"> Some text</label>
     cannot be keyed on the <label>, because filling a keyed element replaces
     its contents and would delete the radio button. The text goes in its own
     <span>, which the engine can fill safely.

  2. NAMED PROTECTED KEYS. Wording that must stay ENGLISH on the Nepali page
     is keyed under a professionalOnly prefix (safeguard.*, consent.*,
     phq9.item*, phq9.scale*, phq9.cutoff*, clinical.*). The prefix is what
     the engine matches, so the key name is deliberate, not a serial number.
"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["referral.html", "phq9.html", "contact.html"]
TEXT_TAGS = {"title", "div", "span", "a", "h1", "h2", "h3", "p", "b", "strong",
             "li", "label", "option", "button", "pre", "i"}
SKIP_TAGS = {"script", "style", "template", "noscript"}
VOID_TAGS = {"meta", "link", "input", "br", "hr", "img", "source", "area"}
CONTROLS = {"input", "select", "textarea", "button"}

# Wording that renders in English on the Nepali page. Keyed by the English
# string itself, so the mapping is readable and a change to the wording is
# visible in the diff.
PROTECTED = {
    "Safeguarding check": "safeguard.checkLabel",
    "This is not a GBV case, not an unaccompanied or separated child, and not an immediate risk to life": "safeguard.confirmation",
    "If you cannot tick this, close the form and use the specialised pathway.": "safeguard.consequence",
    "Consent": "consent.label",
    "The person was told what this is for and agreed to answer": "consent.phq9",
    "Over the last 2 weeks, how often have you been bothered by any of the following problems?": "phq9.itemInstruction",
    "If you checked off any problems, how difficult have these problems made it for you to do your work, take care of things at home, or get along with other people?": "phq9.itemDifficulty",
    "Not difficult at all": "phq9.scaleDifficulty0",
    "Somewhat difficult": "phq9.scaleDifficulty1",
    "Very difficult": "phq9.scaleDifficulty2",
    "Extremely difficult": "phq9.scaleDifficulty3",
}

# Whole-block copy that keeps its own key name for clarity, and stays English.
PROTECTED_BLOCK = {
    "referral.html": {
        "safeguard.referralExclusion": "<b>Three kinds of case do not belong on this form.",
    },
    "phq9.html": {
        "phq9.cutoff.useWarning": "<b>Do not use this to screen a shelter.</b>",
        "clinical.phq9ValidatedTextWarning": "<b>The Nepali text is missing",
        "phq9.cutoff.interpretation": "Bands are the standard PHQ-9 cut-points",
    },
}


class Node:
    def __init__(self, tag, attrs, end_start):
        self.tag = tag
        self.attrs = dict(attrs)
        self.end_start = end_start
        self.end = None
        self.parent = None
        self.children = []
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
        node = Node(tag, attrs, self.source.find(">", self.position()) + 1)
        self.nodes.append(node)
        if self.stack:
            node.parent = self.stack[-1]
            self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
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


def ancestors(node):
    current = node.parent
    while current:
        yield current
        current = current.parent


def descendants(node):
    queue = list(node.children)
    while queue:
        current = queue.pop()
        yield current
        queue.extend(current.children)


def tidy(value):
    return re.sub(r"\s+", " ", value).strip()


def visible_direct_text(node):
    direct = tidy("".join(node.text))
    if not direct or len(direct) < 2:
        return ""
    if re.fullmatch(r"[\W\d\s·—–|/•:,.()\[\]{}+\-*=<>&;#%'\"]+", direct):
        return ""
    return direct


def prefix_for(page):
    return {"referral.html": "ref", "phq9.html": "phq9", "contact.html": "svc"}[page]


def key_page(page):
    path = ROOT / page
    source = path.read_text(encoding="utf-8")
    parser = Parser(source)
    parser.feed(source)
    operations = []
    entries = []
    counter = [0]

    def next_key():
        counter[0] += 1
        return f"{prefix_for(page)}.p{counter[0]:03d}"

    def record(key, english, html=False, protected=False):
        entries.append({"key": key, "en": english, "html": html,
                        "page": page, "protected": protected})

    selected = set()
    for node in parser.nodes:
        if node.tag in SKIP_TAGS or node.tag not in TEXT_TAGS:
            continue
        if not visible_direct_text(node):
            continue
        if "data-i18n" in node.attrs or "data-i18n-skip" in node.attrs:
            continue
        if any(ancestor in selected for ancestor in ancestors(node)):
            continue

        # (1) a <label> that wraps a control: key its own text into a <span>
        if node.tag == "label" and any(child.tag in CONTROLS for child in descendants(node)):
            direct = visible_direct_text(node)
            offset = source.find(direct, node.end_start)
            # only a bare control beside plain text; a label wrapping other
            # markup is handled by the general branch above
            if offset < 0 or any(child.tag not in CONTROLS for child in node.children):
                continue
            key = PROTECTED.get(direct) or next_key()
            selected.add(node)
            record(key, direct, protected=direct in PROTECTED)
            operations.append((offset + len(direct), "</span>"))
            operations.append((offset, '<span data-i18n="%s">' % key))
            continue

        direct = visible_direct_text(node)
        if node.children:
            if node.end is None or any(child.tag in CONTROLS for child in descendants(node)):
                continue
            english = tidy(source[node.end_start:node.end])
            block = PROTECTED_BLOCK.get(page, {})
            key = next(
                (k for k, signature in block.items() if english.startswith(signature)),
                None,
            )
            if key is None:
                key = next_key()
            record(key, english, html=True, protected=key in block)
            operations.append((node.end_start - 1, f' data-i18n="{key}" data-i18n-html'))
            selected.add(node)
            continue

        key = PROTECTED.get(direct, None)
        if key is None:
            key = next_key()
        record(key, direct, protected=direct in PROTECTED)
        operations.append((node.end_start - 1, f' data-i18n="{key}"'))
        selected.add(node)

    # placeholders
    for node in parser.nodes:
        placeholder = node.attrs.get("placeholder")
        if not placeholder or "data-i18n-ph" in node.attrs or "data-i18n-skip" in node.attrs:
            continue
        if (re.fullmatch(r"[A-Z0-9@._+\-X]+", placeholder)
                or re.fullmatch(r"\d{2,4}([-–]\d{1,4})*", placeholder)):
            operations.append((node.end_start - 1, " data-i18n-skip"))
        else:
            key = next_key()
            record(key, placeholder)
            operations.append((node.end_start - 1, f' data-i18n-ph="{key}"'))

    for position, insertion in sorted(operations, reverse=True):
        source = source[:position] + insertion + source[position:]
    path.write_text(source, encoding="utf-8")
    return entries


def key_phq9_javascript(path):
    """The nine items and the four scale labels are built in JavaScript."""
    source = path.read_text(encoding="utf-8")
    entries = []
    items = re.search(r"var ITEMS = \[(.*?)\n  \];", source, re.S).group(1)
    replacements = []
    for number, text in enumerate(re.findall(r'^\s+"(.*?)",?$', items, re.M), start=1):
        key = f"phq9.item{number}"
        entries.append({"key": key, "en": text, "html": False, "page": path.name, "protected": True})
        # the last entry has no trailing comma, so replace the literal itself
        # and let the surrounding punctuation stand
        replacements.append((f'"{text}"', f'{{ key: "{key}", text: "{text}" }}'))
    options = re.search(r"var OPTS = \[(.*?)\n  \];", source, re.S).group(1)
    for index, text in enumerate(re.findall(r'l: "(.*?)"', options)):
        key = f"phq9.scale{index}"
        entries.append({"key": key, "en": text, "html": False, "page": path.name, "protected": True})
        replacements.append((f'{{ v: {index}, l: "{text}" }}',
                             f'{{ v: {index}, key: "{key}", l: "{text}" }}'))
    # the item-9 instruction is minted as a concatenated string in JS. Build
    # the English the same way the JS does, so the dictionary entry is the
    # text the reader actually sees, without the wrapper div.
    instruction = re.search(r"\$\(\"risk\"\)\.innerHTML = '(.*?)';", source, re.S)
    if instruction:
        # The JS concatenates single-quoted fragments; join them the way the
        # browser would, then drop the wrapper element the page supplies.
        joined = re.sub(r"'\s*\+\s*'", "", instruction.group(1)).replace("\\'", "'")
        joined = re.sub(r"^<div[^>]*>", "", joined).strip()
        joined = re.sub(r"</div>\s*$", "", joined).strip()
        text = tidy(joined)
        entries.append({"key": "phq9.item9Instruction", "en": text, "html": True,
                        "page": path.name, "protected": True})
        source = source.replace(
            '$("risk").innerHTML = \'<div class="banner stop" style="margin:14px 0 0">',
            '$("risk").innerHTML = \'<div class="banner stop" style="margin:14px 0 0"'
            ' data-i18n="phq9.item9Instruction">')
        source = source.replace(
            "'positive answer can be audited against whether a referral followed.</div>';",
            "'positive answer can be audited against whether a referral followed.</div>';\n"
            "      if (window.I18N) window.I18N.apply($(\"risk\"));")
    for old, new in replacements:
        if old not in source:
            raise SystemExit(f"could not find in phq9.html: {old[:60]}")
        source = source.replace(old, new, 1)
    path.write_text(source, encoding="utf-8")
    return entries


def main():
    everything = []
    for page in PAGES:
        entries = key_page(page)
        if page == "phq9.html":
            entries += key_phq9_javascript(ROOT / page)
        everything += entries
        print(f"{page}: {len(entries)} keys")
    output = ROOT / "tools" / "new-i18n-entries.json"
    output.write_text(json.dumps(everything, ensure_ascii=False, indent=2), encoding="utf-8")
    protected = [e for e in everything if e["key"].startswith(
        ("phq9.item", "phq9.scale", "phq9.cutoff", "consent.", "safeguard.", "clinical."))]
    print(f"total {len(everything)} keys, {len(protected)} protected")
    print(f"-> {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
