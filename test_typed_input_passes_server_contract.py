"""25 Nov 2026 lesson (review workshop, 24 Nov): the morning QC passed because test values were set by
script, clean, while participants typed on phones and the server refused their entries. This test types
phone-style input into each field form in a real browser (trailing spaces from autocomplete, Enter in long
boxes, Nepali digits, a comma between two phone numbers, a ward written "05", an over-long name, an
upper-case email), saves the record, builds the payload exactly as the page sends it, and checks it with
the server's own validator (snapshot in server-contract/, copied from Thar Lay on 25 Nov 2026).

When the server contract changes, copy the new files into server-contract/ and run this test again.
Needs Playwright with Chromium, and the hub repository checked out beside this one (../hub), because the
pages load ../../hub/assets/*. Without them the test is skipped, like the other hub-dependent tests."""
import datetime, functools, http.server, json, pathlib, socketserver, sys, threading, unittest

HERE = pathlib.Path(__file__).resolve().parent
HUB = HERE.parent / "hub"
sys.path.insert(0, str(HERE / "server-contract"))
try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

MESSY_PHONE = "९८४१२३४५६७, 01-4256909 "


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


@unittest.skipUnless(sync_playwright and HUB.exists(), "needs Playwright and ../hub beside the form repository")
class TypedInputPassesServerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import tempfile, os
        cls.root = pathlib.Path(tempfile.mkdtemp())
        os.symlink(HERE, cls.root / "form")
        os.symlink(HUB, cls.root / "hub")
        cls.srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(_Quiet, directory=str(cls.root)))
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.pw.stop(); cls.srv.shutdown()

    def open(self, page):
        pg = self.browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        local = f"http://127.0.0.1:{self.port}/"
        pg.route("**/*", lambda r: r.continue_() if r.request.url.startswith(local) else r.abort())
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(local + "form/preview/" + page + "?k=test")
        pg.wait_for_timeout(700)
        return pg, errors

    def choose(self, pg, sel_id, value=None):
        pg.wait_for_function(f"(()=>{{const s=document.querySelector('#{sel_id}');return s&&s.options.length>1&&!s.disabled}})()", timeout=5000)
        if value is None:
            value = pg.eval_on_selector(f"#{sel_id}", "s=>[...s.options].map(o=>o.value).find(v=>v&&v!=='OTHER')")
        pg.select_option(f"#{sel_id}", value)
        return value

    def type_into(self, pg, sel, text):
        pg.click(sel); pg.keyboard.type(text)

    def directory_record(self, page, submit):
        import directory2_contract as D
        pg, errors = self.open(page)
        self.choose(pg, "org"); self.choose(pg, "province"); self.choose(pg, "district"); self.choose(pg, "palika")
        self.type_into(pg, "#ward", "05"); pg.click("#placeName")
        pg.keyboard.type("Health Post Dhunche ")
        self.choose(pg, "facility")
        pg.evaluate("setPin(28.1, 85.3, 12.7)")
        pg.check("input[name=services][value='1']")
        pg.check("input[name=gender][value=women]"); pg.check("input[name=age][value='18-59']")
        self.type_into(pg, "#details", "Counselling on Sundays"); pg.keyboard.press("Enter"); pg.keyboard.type("Group sessions ")
        self.type_into(pg, "#refPhone", MESSY_PHONE)
        self.type_into(pg, "#hours", "Sun-Fri 10:00-16:00 ")
        self.choose(pg, "cost")
        pg.check("input[name=status][value=running]"); pg.check("input[name=continuity][value=permanent]")
        self.type_into(pg, "#confName", "Laxman Nath " + "x" * 130)
        self.type_into(pg, "#confRole", "Field coordinator ")
        self.type_into(pg, "#focalEmail", "Laxman.Nath@CMCNepal.org.np ")
        pg.check("#consentPublish"); pg.check("#consentCorrect")
        pg.click(submit); pg.wait_for_timeout(500)
        rec = pg.evaluate("(()=>{const l=read();return l.length?FORM_SEND.payload(l[l.length-1]):null})()")
        pg.close()
        self.assertEqual(errors, [], page)
        self.assertIsNotNone(rec, page + ": the record was not saved")
        return D, rec

    def assert_accepted(self, mod, rec, page):
        try:
            mod.validate_payload(rec)
        except mod.Invalid as e:
            self.fail(f"{page}: the server would refuse this typed entry: {e}\n{json.dumps(rec, ensure_ascii=False)[:600]}")

    def test_directory_signed_in_form(self):
        D, rec = self.directory_record("referral-directory.html", "button[type=submit]")
        self.assert_accepted(D, rec, "referral-directory.html")
        self.assertEqual(rec["refPhone"], "9841234567 / 01-4256909")
        self.assertEqual(rec["ward"], "5")
        self.assertLessEqual(len(rec["confName"]), 120)

    def test_directory_workshop_page(self):
        D, rec = self.directory_record("referral-directory-workshop.html", "#wsSubmit")
        self.assert_accepted(D, rec, "referral-directory-workshop.html")
        self.assertEqual(rec["ward"], "5")

    def test_grief_form(self):
        import grief_contract as G
        pg, errors = self.open("grief-early-assessment.html")
        pg.fill("#date", datetime.date.today().isoformat())
        self.choose(pg, "org"); self.choose(pg, "district", "RAS"); self.choose(pg, "palika", "NP0329403")
        self.assertEqual(pg.eval_on_selector("#ward", "w=>w.max"), "5")  # Uttargaya has 5 wards
        self.type_into(pg, "#ward", "05")
        self.choose(pg, "setting"); self.choose(pg, "worker")
        for name, value in [("consent", "yes"), ("reg", "byname")]:
            pg.check(f"input[name={name}][value={value}]", force=True)
        self.type_into(pg, "#pName", "Sita Tamang ")
        self.type_into(pg, "#pPhone", MESSY_PHONE)
        self.type_into(pg, "#pTime", "evenings ")
        pg.check("input[name=pReach][value=call]", force=True)
        picks = {"sex": "F", "age": "18-59", "living": "home", "disability": "no", "rites": "completed", "functioning": "usual",
                 "beyondExpected": "no", "stateNow": "calm", "selfharm": "no", "childLostCarer": "no", "triage": "normal"}
        for k, v in picks.items():
            pg.check(f"input[name={k}][value='{v}']", force=True)
        for k in ["rx_sad", "rx_yearn", "rx_intrusive", "rx_sleep", "rx_appetite", "rx_concentr", "rx_withdraw", "rx_body", "rx_voice", "rx_anger", "rx_compare"]:
            pg.check(f"input[name={k}][value='1']", force=True)
        for k, v in [("who", "parent"), ("support", "family"), ("needs", "talk"), ("action", "listened")]:
            pg.check(f"input[name={k}][value={v}]", force=True)
        pg.click("button[type=submit]"); pg.wait_for_timeout(500)
        rec = pg.evaluate("(()=>{const l=read();return l.length?FORM_SEND.payload(l[l.length-1]):null})()")
        pg.close()
        self.assertEqual(errors, [])
        self.assertIsNotNone(rec, "the grief record was not saved")
        self.assert_accepted(G, rec, "grief-early-assessment.html")
        self.assertEqual(rec["ward"], "5")
        self.assertEqual(rec["phone"], "9841234567 / 01-4256909")


if __name__ == "__main__":
    unittest.main()
