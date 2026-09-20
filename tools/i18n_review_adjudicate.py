#!/usr/bin/env python3
"""Settle what the project's OWN material settles, and nothing else.

The parent run left 100 keys in English because two independent machine lanes
disagreed, and the project rule forbids deciding a disagreement by a vote.
This run does not vote either. For each disagreement it tries four routes, in
order, and a key only leaves English if one of them succeeds:

  R1  EXACT PHRASE.  The English is a short phrase the project has already
      rendered somewhere reviewable (terminology lock, code list, dictionary
      placeholder). The established rendering is used.

  R2  OBJECTIVE DEFECT.  Exactly one of the two readings is objectively broken
      against the English it must render: it drops or invents an `id=`/`href=`
      the page's script uses, or it leaves Latin words the English did not
      have. That lane is wrong on a fact, not on a preference; the other is
      used. If both lanes are defective the key is held.

  R3  SETTLED TERM.  Align the two readings word for word. Every position that
      differs must be decided by the project's published material: one reading
      uses a word the project already uses for THIS English concept, the other
      uses a word that appears nowhere in the material. Deciding evidence is
      required on both sides -- a word that is absent everywhere, and a
      published word whose own English shares a content word with this key's
      English, so the same spelling for a different concept cannot decide
      anything. Where both readings, or neither, are published, the key is
      held.

  R4  FORMAL ONLY.  The two readings are the same words; they differ only in
      markup or punctuation.

Anything else stays in ENGLISH and is reported with the reason. Nothing here
is a human decision, and every string settled this way remains a `machine`
draft, labelled as such.

The material of "the project's own material" is exactly:
  * hub-real/tools/terminology-lock.json      (approved sentence + code pairs)
  * hub-translation/assets/codes.js           (`np`, `help_np` fields)
  * hub-translation/assets/i18n-strings.js    (shipped placeholders + `ne`)
"""
import difflib
import json
import os
import re

FORM = "/root/mhpss-nepal-work/form-translation"
HUB = "/root/mhpss-nepal-work/hub-translation"
LOCK = "/root/mhpss-nepal-work/hub-real/tools/terminology-lock.json"

DEV = re.compile(r"[\u0900-\u097F]+")
TAG = re.compile(r"<[^>]+>")
LAT = re.compile(r"[A-Za-z]{3,}")
ENW = re.compile(r"[A-Za-z][A-Za-z\-']*")

INVARIANT = ["PHQ-9", "HMIS", "GBV", "IASC", "MHPSS", "WHO", "EDCD", "PRIME", "Kohrt",
             "Kroenke", "Spitzer", "Williams", "Pfizer", "Bikram Sambat", "Rasuwa",
             "Bhote Koshi", "OCMC", "WASH", "PFA", "mhGAP", "NHTC", "IEC", "RDNA",
             "NDRRMA", "CSV", "JSON", "Excel", "Uttargaya", "RB", "AD", "BS", "Nepal",
             "Programme for Improving Mental Health Care", "UK", "Robert", "Janet",
             "Kurt", "Inc"]
STOP = {"with", "that", "this", "from", "have", "been", "will", "your", "they", "them",
        "their", "into", "over", "than", "then", "when", "where", "which", "what",
        "must", "should", "could", "would", "also", "about", "after", "before", "more",
        "most", "only", "some", "such", "each", "other", "same", "person", "people",
        "never", "every", "there", "here", "does", "done", "make", "made"}

SUFFIX = ["हरूलाई", "हरूबाट", "हरूको", "हरूमा", "हरूले", "हरू", "बारे", "सँग", "लाई", "बाट",
          "को", "का", "की", "मा", "ले", "पछि", "भित्र", "सम्म", "तिर"]


def dev_words(v):
    return DEV.findall(TAG.sub(" ", v))


def base_letters(t):
    """Devanagari letters only: matras (U+093E-U+094C), the virama and nukta do
    not count, so a bogus two-letter residue cannot masquerade as a stem."""
    return sum(1 for ch in t if "\u0900" <= ch <= "\u093d")


def stem(t):
    """Strip inflection/plural suffixes, repeatedly, while what is left still
    has at least three Devanagari letters. Returns '' when nothing is left."""
    changed = True
    while changed and base_letters(t) >= 3:
        changed = False
        for s in SUFFIX:
            if t.endswith(s) and base_letters(t[: -len(s)]) >= 3:
                t = t[: -len(s)]
                changed = True
                break
    return t


def stems(v):
    return [stem(t) for t in dev_words(v)]


def morph_family(t):
    """A token and all the inflections our stemmer folds into one."""
    return stem(t) or t


def en_words(v):
    return {w.lower() for w in ENW.findall(TAG.sub(" ", v))} - STOP


# ---------------------------------------------------------------- material
# Evidence for R3 must come from a TERM-LEVEL pair: a code-list label, a
# dictionary placeholder, a short field label. A word taken out of a long
# sentence does not prove what that word means -- `आफैँ` in "sent to the
# register on their own" says nothing about "The person told us" -- so a
# sentence pair must not be allowed to decide an unrelated concept.
TERM_MAX_EN = 5      # content words in the English


def is_term_pair(e, n):
    if "।" in n:                      # a full sentence is not a term
        return False
    if len(en_words(e)) > TERM_MAX_EN:
        return False
    return bool(en_words(e))


def load_material():
    phrase = {}          # lowercased english -> (nepali, source)
    published = {}       # stemmed nepali token -> [(source, english words)]

    def add(en, npv, source):
        e = re.sub(r"\s+", " ", TAG.sub(" ", en)).strip(" .·—–-")
        n = re.sub(r"\s+", " ", TAG.sub(" ", npv)).strip()
        if not e or not n or re.search(r"[A-Za-z]", n):
            return
        phrase.setdefault(e.lower(), (n, source))
        if not is_term_pair(e, n):
            return
        for t in set(dev_words(n)):
            published.setdefault(stem(t), []).append((source, en_words(e)))

    lock = json.load(open(LOCK, encoding="utf-8"))
    for en, npv in lock["by_english"].items():
        add(en, npv, "terminology-lock/by_english")
    for en, v in lock["codes"].items():
        if isinstance(v, dict) and v.get("np"):
            add(en, v["np"], "terminology-lock/codes")

    codes = open(os.path.join(HUB, "assets", "codes.js"), encoding="utf-8").read()
    for m in re.finditer(r'\bname:\s*"((?:[^"\\]|\\.)*)"[^,}]*?\bnp:\s*"((?:[^"\\]|\\.)*)"', codes):
        add(m.group(1), m.group(2), "codes.js/np")
    for m in re.finditer(r'\bname:\s*"((?:[^"\\]|\\.)*)"[^,}]*?\bhelp_np:\s*"((?:[^"\\]|\\.)*)"', codes):
        add(m.group(1), m.group(2), "codes.js/help_np")

    d = open(os.path.join(HUB, "assets", "i18n-strings.js"), encoding="utf-8").read()
    m = re.search(r"\n    placeholders:\s*\{(.*?)\n    \}", d, re.S)
    if m:
        for k, v in re.findall(r'"((?:[^"\\]|\\.)*)"\s*:\s*"((?:[^"\\]|\\.)*)"', m.group(1)):
            add(k, v, "dictionary/placeholders")
    m = re.search(r"\n  ne:\s*\{(.*?)\n  \}", d, re.S)
    body = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)
    body = re.sub(r"//[^\n]*", "", body)
    for k, v in re.findall(r'"((?:[^"\\]|\\.)*)"\s*:\s*"((?:[^"\\]|\\.)*)"', body):
        # The `ne` block keyed by KEY, not by English, so it carries no
        # English of its own here. Gather its tokens separately: it proves a
        # word is in use, but it can never prove a meaning, so it does not
        # count as a publisher for R3.
        for t in set(dev_words(v)):
            published.setdefault(stem(t), []).append(("dictionary/ne", set()))
    return phrase, published


def published_for(token, key_english, published):
    """Sources that publish this token for an English sharing a content word
    with the key's English. Empty means it is not published FOR THIS meaning
    (even if the same spelling appears somewhere else)."""
    out = []
    for source, enw in published.get(token, []):
        if enw & key_english:
            out.append(source)
    return out


def stray_latin(v, en):
    have = {w.lower() for w in LAT.findall(TAG.sub(" ", en))}
    t = TAG.sub(" ", v)
    for tok in INVARIANT:
        t = re.sub(re.escape(tok), " ", t, flags=re.I)
    return [w for w in LAT.findall(t) if w.lower() not in have]


def attrs(v):
    return (sorted(re.findall(r'id="([^"]*)"', v)),
            sorted(re.findall(r'href="([^"]*)"', v)))


def main():
    phrase, published = load_material()
    entries = json.load(open(os.path.join(FORM, "tools", "translatable.json"), encoding="utf-8"))
    idx = {e["key"]: e for e in entries}
    hdr = json.load(open(os.path.join(FORM, "tools", "i18n-ne-human-decision-required.json"),
                         encoding="utf-8"))

    settled, held = {}, {}
    for key in sorted(hdr):
        en = hdr[key]["english"]
        a, b = hdr[key].get("lane-A", ""), hdr[key].get("lane-B", "")
        page = hdr[key].get("page", idx.get(key, {}).get("page", ""))
        key_en = en_words(en)

        def keep(npv, reason):
            settled[key] = {"page": page, "np": npv, "reason": reason, "english": en}

        bare = re.sub(r"\s+", " ", TAG.sub(" ", en)).strip(" .·—–-").lower()
        if bare in phrase and len(en.split()) <= 12:
            npv, source = phrase[bare]
            keep(npv, "R1 the project has already rendered this exact phrase (%s)" % source)
            continue

        # R1b -- the English is built from parts the project has already
        # rendered (the trial banner is "Revised draft for field piloting" +
        # "· saved on this phone, sent to the coordination register when there
        # is signal", both published verbatim). If one reading's words are
        # exactly the published parts joined, use that reading; its markup is
        # then the page's own and the authority supplies the vocabulary.
        parts = [p.strip(" .·—–-") for p in re.split(r"·", re.sub(r"\s+", " ", TAG.sub(" ", en)))]
        if len(parts) > 1 and all(p.lower() in phrase for p in parts if p):
            composed = "·".join(phrase[p.lower()][0] for p in parts if p)
            norm = lambda s: re.sub(r"\s+", "", TAG.sub("", s)).replace("·", "")
            if a and norm(a) == norm(composed):
                keep(a, "R1b every part of this English is already rendered by the project, "
                        "and this reading uses exactly those parts")
                continue
            if b and norm(b) == norm(composed):
                keep(b, "R1b every part of this English is already rendered by the project, "
                        "and this reading uses exactly those parts")
                continue

        if a and b:
            bad_a = (attrs(a) != attrs(en)) or bool(stray_latin(a, en))
            bad_b = (attrs(b) != attrs(en)) or bool(stray_latin(b, en))
            if bad_a != bad_b:
                winner = b if bad_a else a
                keep(winner, "R2 the other reading is objectively broken against the English "
                             "it must render")
                continue

        if not a or not b:
            held[key] = {"page": page, "reason": "a lane produced nothing", "english": en}
            continue

        sa, sb = stems(a), stems(b)
        if sa == sb:
            keep(a if len(a) <= len(b) else b,
                 "R4 the two readings are the same words up to inflection, markup or "
                 "punctuation")
            continue

        sm = difflib.SequenceMatcher(a=sa, b=sb, autojunk=False)
        ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
        ok, est_a, est_b, why = True, 0, 0, []
        for tag, i1, i2, j1, j2 in ops:
            if tag != "replace" or (i2 - i1) != (j2 - j1):
                ok = False
                why.append("a word is added or dropped")
                continue
            for ta, tb in zip(sa[i1:i2], sb[j1:j2]):
                pa = published_for(ta, key_en, published)
                pb = published_for(tb, key_en, published)
                in_a = ta in published
                in_b = tb in published
                if pa and not in_b:
                    est_a += 1
                    why.append("'%s' [%s] is the established word; '%s' is not in the "
                               "material at all" % (ta, ", ".join(sorted(set(pa))), tb))
                elif pb and not in_a:
                    est_b += 1
                    why.append("'%s' [%s] is the established word; '%s' is not in the "
                               "material at all" % (tb, ", ".join(sorted(set(pb))), ta))
                elif in_a or in_b:
                    ok = False
                    why.append("both '%s' and '%s' appear in the material" % (ta, tb))
                else:
                    ok = False
                    why.append("neither '%s' nor '%s' is published for this English" % (ta, tb))
        if ok and est_a and not est_b:
            keep(a, "R3 terminology: " + "; ".join(why))
        elif ok and est_b and not est_a:
            keep(b, "R3 terminology: " + "; ".join(why))
        else:
            held[key] = {"page": page, "english": en,
                         "reason": "; ".join(why) or "not settled by the project's material"}

    print("flagged keys:                                 %d" % len(hdr))
    print("settled by the project's own material:        %d" % len(settled))
    print("left in English -- no authority settles them: %d" % len(held))
    print()
    for k in sorted(settled):
        print("  SETTLED %-12s %s" % (k, settled[k]["reason"]))
    print()
    # a full audit dump: every settlement with both readings, and every held
    # key with the reason, so a reviewer reads evidence rather than prose
    audit = {"settled": {}, "held": {}}
    for k in sorted(settled):
        audit["settled"][k] = dict(settled[k], lane_A=hdr[k].get("lane-A", ""),
                                   lane_B=hdr[k].get("lane-B", ""))
    for k in sorted(held):
        audit["held"][k] = dict(held[k], lane_A=hdr[k].get("lane-A", ""),
                                lane_B=hdr[k].get("lane-B", ""))
    json.dump(audit, open(os.path.join(FORM, "tools", "i18n-review-evidence.json"), "w",
                          encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    json.dump(settled, open(os.path.join(FORM, "tools", "i18n-ne-authority-resolved.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    json.dump(held, open(os.path.join(FORM, "tools", "i18n-ne-authority-held.json"), "w",
                         encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
