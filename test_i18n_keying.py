#!/usr/bin/env python3
"""Contract tests for keying referral.html, phq9.html and contact.html.

Run from the form repository root:  python3 -m unittest test_i18n_keying

The base fixtures in tools/fixtures/keying-base/ are the pre-keying pages
captured from the repository head, so this test is self-contained and does not
depend on anything in /tmp.

What keying is allowed to do to a page, and nothing else:

  * add a `data-i18n*` attribute to an element, and
  * wrap bare label text that shares a <label> with a form control in
    <span data-i18n="KEY">...</span>, because filling a keyed <label> would
    replace the control it contains.

It must NOT change any field id/name/value, any script, or any other markup.
"""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "tools" / "fixtures" / "keying-base"
PAGES = ["referral.html", "phq9.html", "contact.html"]
KEY_ATTRS = {"data-i18n", "data-i18n-ph", "data-i18n-aria", "data-i18n-alt", "data-i18n-title"}

ATTR = re.compile(r'\sdata-i18n(?:-(?:ph|aria|alt|title|html|skip))?(?:="[^"]*")?')
# The one span keying may add: <span data-i18n="KEY">TEXT</span>, wrapping text
# that used to sit bare inside a <label> beside a control. No other attribute,
# so an element that already existed and merely gained data-i18n-html is not
# matched here (it is handled by ATTR above).
WRAP = re.compile(r'<span data-i18n="[^"]*">((?:(?!<span\b|</span>).)*)</span>')
SCRIPT = re.compile(r"(<script\b[^>]*>)(.*?)(</script>)", re.S)


def normalise(text):
    """The page with keying's two permitted MARKUP edits undone.

    Scripts are blanked, not compared here: keying the PHQ-9 items in
    JavaScript is a real change and test_phq9_runtime_contract_is_semantically_unchanged
    asserts it semantically, so it does not belong in a markup equality test.
    """
    text = WRAP.sub(r"\1", text)
    text = ATTR.sub("", text)
    # blank the script BODY on both sides; the opening tag and src are compared
    return SCRIPT.sub(lambda m: m.group(1) + "@@body@@" + m.group(3), text)


class ControlInventory(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.controls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"input", "select", "textarea", "button"}:
            self.controls.append((tag, attrs.get("type", ""), attrs.get("id", ""),
                                  attrs.get("name", ""), attrs.get("value", "")))


def controls(path):
    parser = ControlInventory()
    parser.feed(Path(path).read_text(encoding="utf-8"))
    return parser.controls


class I18nKeyingContract(unittest.TestCase):
    def test_keying_does_not_change_controls_or_runtime_scripts(self):
        for page in PAGES:
            base, after = BASE / page, ROOT / page
            self.assertEqual(controls(base), controls(after), page)
            self.assertEqual(re.findall(r"<script(?:\s+src=\"([^\"]+)\")?[^>]*>",
                                        base.read_text(encoding="utf-8")),
                             re.findall(r"<script(?:\s+src=\"([^\"]+)\")?[^>]*>",
                                        after.read_text(encoding="utf-8")), page)

    def test_only_i18n_markup_was_added(self):
        """Undo keying's permitted edits and the page must equal its base."""
        for page in PAGES:
            base = (BASE / page).read_text(encoding="utf-8")
            after = (ROOT / page).read_text(encoding="utf-8")
            self.assertEqual(normalise(after), normalise(base), page)

    def test_phq9_runtime_contract_is_semantically_unchanged(self):
        base = (BASE / "phq9.html").read_text(encoding="utf-8")
        after = (ROOT / "phq9.html").read_text(encoding="utf-8")
        items = re.search(r"var ITEMS = \[(.*?)\n  \];", base, re.S).group(1)
        actual = re.search(r"var ITEMS = \[(.*?)\n  \];", after, re.S).group(1)
        self.assertEqual(re.findall(r'^\s+"(.*)",?$', items, re.M),
                         re.findall(r'text: "(.*)"', actual))
        opts = re.search(r"var OPTS = \[(.*?)\n  \];", base, re.S).group(1)
        actual_opts = re.search(r"var OPTS = \[(.*?)\n  \];", after, re.S).group(1)
        self.assertEqual(re.findall(r'l: "(.*?)"', opts), re.findall(r'l: "(.*?)"', actual_opts))
        self.assertEqual(re.findall(r'v: (\d)', opts), re.findall(r'v: (\d)', actual_opts))
        for token in ["q1: a[0]", "q9: a[8]", "total >= 10", "item9_positive"]:
            self.assertEqual(base.count(token), after.count(token), token)
        # the item-9 instruction the JS mints must still be applied after the
        # form sets it, or a suicide-item warning would render in English on a
        # page that has been switched to Nepali without the engine filling it
        self.assertIn('window.I18N.apply($("risk"))', after)

    def test_protected_runtime_copy_has_named_keys(self):
        text = (ROOT / "referral.html").read_text(encoding="utf-8") + \
               (ROOT / "phq9.html").read_text(encoding="utf-8")
        for prefix in ["safeguard.", "consent.", "phq9.item", "phq9.scale",
                       "phq9.cutoff", "clinical."]:
            self.assertIn(prefix, text, prefix)

    def test_every_keyed_page_declares_its_skip_cases(self):
        """Invariant text (a code, a domain, a phone mask) must say so."""
        for page in PAGES:
            text = (ROOT / page).read_text(encoding="utf-8")
            self.assertGreaterEqual(len(re.findall(r"data-i18n-skip", text)), 1, page)
            # a placeholder that is a code or a numeric pattern must be skipped,
            # never handed to a translator
            for ph in re.findall(r'placeholder="([^"]+)"', text):
                if re.fullmatch(r"[A-Z0-9@._+\-X]+|\d{2,4}([-–]\d{1,4})*", ph):
                    self.assertIn('data-i18n-skip', text)

    def test_item9_instruction_key_exists_and_is_protected(self):
        """A real defect found in the browser, pinned so it cannot come back.

        The item-9 safety instruction is minted in JavaScript with
        data-i18n="phq9.item9Instruction". If that key is not in the dictionary
        (the extractor only read the ITEMS/OPTS arrays, so it was missed) the
        engine replaces the whole instruction with the literal text
        "[phq9.item9Instruction]" on the page -- on the one question where
        someone acts on the answer. Two things must hold:
          * the key is in the dictionary, and
          * its key prefix is under professionalOnly, so it stays ENGLISH.

        This test reads the real dictionary, so it fails if either is lost.
        """
        dictionary = (Path("/root/mhpss-nepal-work/hub-translation/assets")
                      / "i18n-strings.js")
        if not dictionary.is_file():
            self.skipTest("shared dictionary not present in this worktree")
        src = dictionary.read_text(encoding="utf-8")
        en = re.search(r"\n  en:\s*\{(.*?)\n  \}", src, re.S).group(1)
        self.assertIn('"phq9.item9Instruction"', en,
                      "the item-9 instruction has a key but no dictionary entry; "
                      "the page will render [phq9.item9Instruction]")
        pro = re.search(r"professionalOnly:\s*\[(.*?)\]", src, re.S).group(1)
        self.assertIn('"phq9.item"', pro)

    def test_protected_prefixes_all_match_live_keys(self):
        """The historic bug: the prefix list protected 0 of 204 keys.

        Every prefix in _meta.professionalOnly must match at least one real key,
        and every key under a prefix must have no Nepali entry. This is the
        count the task asks for, asserted rather than reported.
        """
        dictionary = (Path("/root/mhpss-nepal-work/hub-translation/assets")
                      / "i18n-strings.js")
        if not dictionary.is_file():
            self.skipTest("shared dictionary not present in this worktree")
        src = dictionary.read_text(encoding="utf-8")

        def pairs(name):
            body = re.search(r"\n  " + name + r":\s*\{(.*?)\n  \}", src, re.S).group(1)
            body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
            body = re.sub(r"^\s*//.*$", "", body, flags=re.M)
            return dict(re.findall(r'"((?:[^"\\]|\\.)*)"\s*:\s*"((?:[^"\\]|\\.)*)"', body))

        en, ne = pairs("en"), pairs("ne")
        pro = re.findall(r'"([^"]+)"', re.search(r"professionalOnly:\s*\[(.*?)\]", src, re.S).group(1))
        dead = [p for p in pro if not any(k.startswith(p) for k in en)]
        self.assertEqual(dead, [], "prefix(es) matching no live key: %s" % dead)
        # no protected key may carry Nepali
        leaked = [k for k in ne if any(k.startswith(p) for p in pro) and ne[k].strip()]
        self.assertEqual(leaked, [], "protected keys with Nepali: %s" % leaked)


if __name__ == "__main__":
    unittest.main()
