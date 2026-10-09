/* =====================================================================
   MHPSS Nepal — controlled vocabularies
   ---------------------------------------------------------------------
   PROVENANCE. Every list below is derived from records already held by
   the response, not invented. Since 16 Sep 2026 the lists follow the data
   workstream's code lists of 15 Sep 2026 (workbook "MHPSS Nepal code
   lists": sheets Sites, Palikas, Districts, Organisations, Activities and
   the 47-item delta list), source references [S1]..[S22] as in that
   workbook:
     - SITES      : the holding-centre roster sheet of the daily reporting
                    workbook (23, source:"roster"), sites named in submitted
                    reports but not on that roster (31, "reported"), the DAO
                    Nuwakot list of 29 Bhadra 2083 (12, "gov-list"), and 8
                    codes retired or merged, kept only so old records resolve.
     - PALIKAS    : the 16 local levels that appear in reports or on the
                    Ward counts for Aamachhodingmo (5), Shahid Lakhan (9), Gandaki (8) and
                    Ichchhakamana (7) added 20 Sep 2026, each confirmed from at least two
                    independent sources (Shahid Lakhan from its own municipal website). The
                    other 16 came with the original list.
                    roster, keyed by the OCHA COD-AB Nepal v02 adm3 P-code
                    (HDX cod-ab-npl, Survey Department and UN RCO; valid from
                    14 Mar 2024, last updated 14 Aug 2026).
     - ORGS       : provider names actually appearing in submitted reports;
                    official names where the workstream verified them.
     - ACTIVITIES : the activity list agreed 17 Sep 2026 -- plain labels on
                    the form, IASC layer and 4Ws 2012 subcodes in the
                    backend, one code for both; the previous list is kept
                    as ACTIVITIES_V03 with its crosswalk.
     - DISTRICTS / TARGET GROUPS / CADRES : standard operational categories.

   Anything unverified is marked. Open questions are listed in META and in
   the block they concern. Nothing here should be treated as an agreed list
   until the MHPSS Technical Working Group and EDCD have signed it off.
   ===================================================================== */

const META = {
  version: "0.4.0-draft",
  compiled: "2026-09-17",
  basis: "Data workstream code lists of 15 Sep 2026 and delta list D-S01..D-M07; palika P-codes from OCHA COD-AB NPL v02; EDCD review of 17 Sep 2026 (cadre list, service settings, districts); districts from the RDNA Rasuwa-Bhotekoshi Flood 2026 (NDRRMA/NPC) and NDRRMA SitRep #1 of 1 Sep 2026; activity list v3 of 17 Sep 2026 (layer.item codes on the IASC pyramid, 4Ws 2012 subcodes in the backend)",
  status: "DRAFT — not agreed with EDCD or the MHPSS Technical Working Group",
  /* held open, not decided here: see the block each one concerns */
  questions: ["D-S14", "D-S23", "D-O02", "D-C01", "D-C02", "D-A03", "D-A05"],
};

/* ---------------------------------------------------------------------
   DISTRICTS
   `province` from the workstream's Districts sheet [S7]: Bagmati except NAW. NAW carries the official name and keeps
   "Nawalpur" as an alias because partners write it [D-S24]. SIN added for
   one KOSHISH record at Chautara Hospital [D-S25] -- whether that record is
   part of the flood response is an open question (D-S23), so the district
   exists but is not treated as a response district.
   ------------------------------------------------------------------- */
const DISTRICTS = [
  { code: "RAS", pcode: "NP0329", name: "Rasuwa", province: "Bagmati", np: "रसुवा", np_src: "draft" },
  { code: "NUW", pcode: "NP0328", name: "Nuwakot", province: "Bagmati", np: "नुवाकोट", np_src: "draft" },
  { code: "DHA", pcode: "NP0330", name: "Dhading", province: "Bagmati", np: "धादिङ", np_src: "draft" },
  { code: "KTM", pcode: "NP0327", name: "Kathmandu", province: "Bagmati", np: "काठमाडौं", np_src: "draft" },
  { code: "CHT", pcode: "NP0335", name: "Chitwan", province: "Bagmati", np: "चितवन", np_src: "draft" },
  { code: "NAW", pcode: "NP0447", name: "Nawalparasi (Bardaghat Susta East)", alias: "Nawalpur", province: "Gandaki", np: "नवलपरासी (बर्दघाट सुस्ता पूर्व)", np_src: "draft" },
  { code: "SIN", pcode: "NP0323", name: "Sindhupalchok", province: "Bagmati", np: "सिन्धुपाल्चोक", np_src: "draft", question: "D-S23" },
  /* Added 17 Sep 2026: Gorkha named by EDCD in the review and listed as a
     core assessment district in the RDNA (local levels Shahid Lakhan and
     Gandaki RMs); Tanahun listed in the RDNA "where information available"
     and in NDRRMA SitRep #1 (missing persons). Their palikas follow once the
     COD-AB P-codes are handed over. */
  { code: "GOR", pcode: "NP0436", name: "Gorkha", province: "Gandaki", np: "गोरखा", np_src: "draft", src: "EDCD review 17 Sep 2026; RDNA 2026; NDRRMA SitRep #1" },
  { code: "TAN", pcode: "NP0440", name: "Tanahun", province: "Gandaki", np: "तनहुँ", np_src: "draft", src: "RDNA 2026; NDRRMA SitRep #1" },
  { code: "OTH", name: "Other — specify", np: "अन्य — उल्लेख गर्नुहोस्", np_src: "draft" },

  /* ---- country-wide districts, added 21 Sep 2026 on the Ministry's
     decision that every province must be selectable, not only the
     flood-affected ones. Codes above are unchanged; these are new.
     Nepali names are pending: np_src marks them so the interface can
     fall back to English rather than show a guessed name. */
  { code: "TAP", name: "Taplejung", province: "Koshi", pcode: "NP0101", np_src: "pending" },
  { code: "PAN", name: "Panchthar", province: "Koshi", pcode: "NP0102", np_src: "pending" },
  { code: "ILA", name: "Ilam", province: "Koshi", pcode: "NP0103", np_src: "pending" },
  { code: "JHA", name: "Jhapa", province: "Koshi", pcode: "NP0104", np_src: "pending" },
  { code: "MOR", name: "Morang", province: "Koshi", pcode: "NP0105", np_src: "pending" },
  { code: "SUN", name: "Sunsari", province: "Koshi", pcode: "NP0106", np_src: "pending" },
  { code: "DHAN", name: "Dhankuta", province: "Koshi", pcode: "NP0107", np_src: "pending" },
  { code: "TER", name: "Terhathum", province: "Koshi", pcode: "NP0108", np_src: "pending" },
  { code: "SAN", name: "Sankhuwasabha", province: "Koshi", pcode: "NP0109", np_src: "pending" },
  { code: "BHO", name: "Bhojpur", province: "Koshi", pcode: "NP0110", np_src: "pending" },
  { code: "SOL", name: "Solukhumbu", province: "Koshi", pcode: "NP0111", np_src: "pending" },
  { code: "KHO", name: "Khotang", province: "Koshi", pcode: "NP0112", np_src: "pending" },
  { code: "OKH", name: "Okhaldhunga", province: "Koshi", pcode: "NP0113", np_src: "pending" },
  { code: "UDA", name: "Udayapur", province: "Koshi", pcode: "NP0114", np_src: "pending" },
  { code: "SAP", name: "Saptari", province: "Madhesh", pcode: "NP0215", np_src: "pending" },
  { code: "SIR", name: "Siraha", province: "Madhesh", pcode: "NP0216", np_src: "pending" },
  { code: "DHANU", name: "Dhanusha", province: "Madhesh", pcode: "NP0217", np_src: "pending", alias: ["Dhanusa"] },
  { code: "MAH", name: "Mahottari", province: "Madhesh", pcode: "NP0218", np_src: "pending" },
  { code: "SAR", name: "Sarlahi", province: "Madhesh", pcode: "NP0219", np_src: "pending" },
  { code: "RAU", name: "Rautahat", province: "Madhesh", pcode: "NP0232", np_src: "pending" },
  { code: "BAR", name: "Bara", province: "Madhesh", pcode: "NP0233", np_src: "pending" },
  { code: "PAR", name: "Parsa", province: "Madhesh", pcode: "NP0234", np_src: "pending" },
  { code: "SIND", name: "Sindhuli", province: "Bagmati", pcode: "NP0320", np_src: "pending" },
  { code: "RAM", name: "Ramechhap", province: "Bagmati", pcode: "NP0321", np_src: "pending" },
  { code: "DOL", name: "Dolakha", province: "Bagmati", pcode: "NP0322", np_src: "pending" },
  { code: "KAV", name: "Kavre", province: "Bagmati", pcode: "NP0324", np_src: "pending", alias: ["Kavrepalanchok"] },
  { code: "LAL", name: "Lalitpur", province: "Bagmati", pcode: "NP0325", np_src: "pending" },
  { code: "BHA", name: "Bhaktapur", province: "Bagmati", pcode: "NP0326", np_src: "pending" },
  { code: "MAK", name: "Makwanpur", province: "Bagmati", pcode: "NP0331", np_src: "pending" },
  { code: "LAM", name: "Lamjung", province: "Gandaki", pcode: "NP0437", np_src: "pending" },
  { code: "MAN", name: "Manang", province: "Gandaki", pcode: "NP0438", np_src: "pending" },
  { code: "KAS", name: "Kaski", province: "Gandaki", pcode: "NP0439", np_src: "pending" },
  { code: "SYA", name: "Syangja", province: "Gandaki", pcode: "NP0441", np_src: "pending" },
  { code: "PARB", name: "Parbat", province: "Gandaki", pcode: "NP0442", np_src: "pending" },
  { code: "BAG", name: "Baglung", province: "Gandaki", pcode: "NP0443", np_src: "pending" },
  { code: "MYA", name: "Myagdi", province: "Gandaki", pcode: "NP0444", np_src: "pending" },
  { code: "MUS", name: "Mustang", province: "Gandaki", pcode: "NP0445", np_src: "pending" },
  { code: "PAL", name: "Palpa", province: "Lumbini", pcode: "NP0546", np_src: "pending" },
  { code: "NAWAL", name: "Nawalparasi West", province: "Lumbini", pcode: "NP0547", np_src: "pending" },
  { code: "RUP", name: "Rupandehi", province: "Lumbini", pcode: "NP0548", np_src: "pending" },
  { code: "KAP", name: "Kapilvastu", province: "Lumbini", pcode: "NP0549", np_src: "pending", alias: ["Kapilbastu"] },
  { code: "ARG", name: "Arghakhanchi", province: "Lumbini", pcode: "NP0550", np_src: "pending" },
  { code: "GUL", name: "Gulmi", province: "Lumbini", pcode: "NP0551", np_src: "pending" },
  { code: "RUK", name: "Rukum East", province: "Lumbini", pcode: "NP0552", np_src: "pending" },
  { code: "ROL", name: "Rolpa", province: "Lumbini", pcode: "NP0554", np_src: "pending" },
  { code: "PYU", name: "Pyuthan", province: "Lumbini", pcode: "NP0555", np_src: "pending" },
  { code: "DAN", name: "Dang", province: "Lumbini", pcode: "NP0556", np_src: "pending" },
  { code: "BAN", name: "Banke", province: "Lumbini", pcode: "NP0557", np_src: "pending" },
  { code: "BARD", name: "Bardiya", province: "Lumbini", pcode: "NP0558", np_src: "pending" },
  { code: "RUKU", name: "Rukum West", province: "Karnali", pcode: "NP0652", np_src: "pending" },
  { code: "SAL", name: "Salyan", province: "Karnali", pcode: "NP0653", np_src: "pending" },
  { code: "SUR", name: "Surkhet", province: "Karnali", pcode: "NP0659", np_src: "pending" },
  { code: "JAJ", name: "Jajarkot", province: "Karnali", pcode: "NP0660", np_src: "pending" },
  { code: "DAI", name: "Dailekh", province: "Karnali", pcode: "NP0661", np_src: "pending" },
  { code: "DOLP", name: "Dolpa", province: "Karnali", pcode: "NP0662", np_src: "pending" },
  { code: "JUM", name: "Jumla", province: "Karnali", pcode: "NP0663", np_src: "pending" },
  { code: "KAL", name: "Kalikot", province: "Karnali", pcode: "NP0664", np_src: "pending" },
  { code: "MUG", name: "Mugu", province: "Karnali", pcode: "NP0665", np_src: "pending" },
  { code: "HUM", name: "Humla", province: "Karnali", pcode: "NP0666", np_src: "pending" },
  { code: "BAJ", name: "Bajhang", province: "Sudur Paschim", pcode: "NP0767", np_src: "pending" },
  { code: "BAJU", name: "Bajura", province: "Sudur Paschim", pcode: "NP0768", np_src: "pending" },
  { code: "ACH", name: "Achham", province: "Sudur Paschim", pcode: "NP0769", np_src: "pending" },
  { code: "DOT", name: "Doti", province: "Sudur Paschim", pcode: "NP0770", np_src: "pending" },
  { code: "KAI", name: "Kailali", province: "Sudur Paschim", pcode: "NP0771", np_src: "pending" },
  { code: "KAN", name: "Kanchanpur", province: "Sudur Paschim", pcode: "NP0772", np_src: "pending" },
  { code: "DAD", name: "Dadeldhura", province: "Sudur Paschim", pcode: "NP0773", np_src: "pending" },
  { code: "BAI", name: "Baitadi", province: "Sudur Paschim", pcode: "NP0774", np_src: "pending" },
  { code: "DAR", name: "Darchula", province: "Sudur Paschim", pcode: "NP0775", np_src: "pending" },
];

/* ---------------------------------------------------------------------
   PALIKAS  [D-S26]
   The 16 local levels that appear in submitted reports or on the roster.
   Official English and Devanagari names from the data workstream's code
   list (sources S3 MoFAGA booklet, S4 MoFAGA contact lists, S5 NSO census
   ward table, S6 NHFR, S8 local-government sites). `pcode` is the OCHA
   COD-AB Nepal v02 adm3 P-code -- the humanitarian join key, the one the
   NDRRMA 5W and any map will match on. It is the KEY of this list: no
   second identifier to keep in step.
   A record that names only a palika and no site is coded at palika level
   (a substantial share of the backlog records do); a palika is not a site and never
   enters the roster denominator.
   ------------------------------------------------------------------- */
const PALIKAS = [
  { pcode: "NP0329403", name: "Uttargaya Rural Municipality", np: "उत्तरगया गाउँपालिका", type: "RM", wards: 5, district: "RAS", province: "Bagmati", src: "[S3][S5][S6][S8]; pcode COD-AB NPL v02" },
  { pcode: "NP0329402", name: "Gosaikunda Rural Municipality", np: "गोसाईकुण्ड गाउँपालिका", type: "RM", wards: 6, district: "RAS", province: "Bagmati", src: "[S3][S5][S6][S8]; pcode COD-AB NPL v02" },
  { pcode: "NP0329404", name: "Kalika Rural Municipality", np: "कालिका गाउँपालिका", type: "RM", wards: 5, district: "RAS", province: "Bagmati", src: "[S3][S5][S6][S8]; pcode COD-AB NPL v02" },
  /* Added 17 Sep 2026 from the official list of affected local levels in the
     RDNA Rasuwa-Bhotekoshi Flood 2026 (NDRRMA / NPC). P-codes as the COD-AB
     NPL v02 file names them (read the same day); ward counts and Devanagari
     spellings are drafts until the data workstream's code-list ruling
     confirms them. Shivapuri RM (Nuwakot, NDRRMA SitRep #1) is NOT added:
     COD-AB carries two units of that name in Nuwakot (NP0328410, NP0328596)
     and does not say which is the rural municipality -- a ruling first. */
  { pcode: "NP0329401", alias: "Parbatikunda", name: "Aamachhodingmo Rural Municipality", np: "आमाछोदिङमो गाउँपालिका", type: "RM", wards: 5, district: "RAS", province: "Bagmati", np_src: "draft", src: "RDNA 2026; NDRRMA SitRep #1; pcode COD-AB NPL v02 (17 Sep)" },
  { pcode: "NP0436408", name: "Shahid Lakhan Rural Municipality", np: "शहीद लखन गाउँपालिका", type: "RM", wards: 9, district: "GOR", province: "Gandaki", np_src: "draft", src: "RDNA 2026; pcode COD-AB NPL v02 (17 Sep)" },
  { pcode: "NP0436409", name: "Gandaki Rural Municipality", np: "गण्डकी गाउँपालिका", type: "RM", wards: 8, district: "GOR", province: "Gandaki", np_src: "draft", src: "RDNA 2026; pcode COD-AB NPL v02 (17 Sep)" },
  { pcode: "NP0335401", name: "Ichchhakamana Rural Municipality", alias: "Ichchha Kamana", np: "इच्छाकामना गाउँपालिका", type: "RM", wards: 7, district: "CHT", province: "Bagmati", np_src: "draft", src: "RDNA 2026; pcode COD-AB NPL v02 (17 Sep), spelt Ichchha Kamana there" },
  { pcode: "NP0328301", name: "Bidur Municipality", np: "विदुर नगरपालिका", type: "M", wards: 13, district: "NUW", province: "Bagmati", src: "[S3][S4][S5][S6]; pcode COD-AB NPL v02" },
  { pcode: "NP0328302", name: "Belkotgadhi Municipality", np: "बेलकोटगढी नगरपालिका", type: "M", wards: 13, district: "NUW", province: "Bagmati", src: "[S3][S5][S6][S8]; pcode COD-AB NPL v02" },
  { pcode: "NP0328402", name: "Kispang Rural Municipality", np: "किस्पाङ गाउँपालिका", type: "RM", wards: 5, district: "NUW", province: "Bagmati", src: "[S3][S5][S6][S8]; pcode COD-AB NPL v02" },
  { pcode: "NP0328406", name: "Likhu Rural Municipality", np: "लिखु गाउँपालिका", type: "RM", wards: 6, district: "NUW", province: "Bagmati", src: "[S3][S5][S6][S8]; pcode COD-AB NPL v02" },
  { pcode: "NP0328403", name: "Tarakeshwor Rural Municipality", np: "तारकेश्वर गाउँपालिका", type: "RM", wards: 6, district: "NUW", province: "Bagmati", src: "[S3][S4][S5][S6]; pcode COD-AB NPL v02" },
  { pcode: "NP0330410", name: "Galchhi Rural Municipality", np: "गल्छी गाउँपालिका", type: "RM", wards: 8, district: "DHA", province: "Bagmati", src: "[S3][S5][S6][S8]; pcode COD-AB NPL v02" },
  { pcode: "NP0330409", name: "Gajuri Rural Municipality", np: "गजुरी गाउँपालिका", type: "RM", wards: 8, district: "DHA", province: "Bagmati", src: "[S3][S5][S6][S8]; pcode COD-AB NPL v02" },
  { pcode: "NP0330408", name: "Benighat Rorang Rural Municipality", np: "बेनीघाट रोराङ्ग गाउँपालिका", type: "RM", wards: 10, district: "DHA", province: "Bagmati", src: "[S3][S5][S6][S8]; pcode COD-AB NPL v02" },
  { pcode: "NP0330407", name: "Siddhalek Rural Municipality", np: "सिद्धलेक गाउँपालिका", type: "RM", wards: 7, district: "DHA", province: "Bagmati", src: "[S3][S5][S6][S8]; pcode COD-AB NPL v02" },
  { pcode: "NP0327101", name: "Kathmandu Metropolitan City", np: "काठमाडौं महानगरपालिका", type: "MC", wards: 32, district: "KTM", province: "Bagmati", src: "[S3][S5][S6][S8]; pcode COD-AB NPL v02" },
  { pcode: "NP0335101", name: "Bharatpur Metropolitan City", np: "भरतपुर महानगरपालिका", type: "MC", wards: 29, district: "CHT", province: "Bagmati", src: "[S3][S4][S5][S6]; pcode COD-AB NPL v02" },
  { pcode: "NP0447301", name: "Madhya Bindu Municipality", np: "मध्यविन्दु नगरपालिका", type: "M", wards: 15, district: "NAW", province: "Gandaki", src: "[S3][S4][S5][S8]; pcode COD-AB NPL v02" },
  { pcode: "NP0323302", name: "Choutara Sangachowkgadhi Municipality", np: "चौतारा साँगाचोकगढी नगरपालिका", type: "M", wards: 14, district: "SIN", province: "Bagmati", src: "[S3][S5][S6][S8]; pcode COD-AB NPL v02" },
  /* ---- country-wide local levels, MoFAGA official list, added 21 Sep
     2026. Codes are "MF"+the MoFAGA number, NOT COD-AB pcodes: the two
     systems are different and must not be mixed, so nothing can join on
     these by mistake. `mofaga` keeps the raw number. No ward counts are
     given here because the list has none -- the ward picker stays hidden
     rather than offering numbers that do not exist. */
  { pcode: "MF10101", mofaga: "10101", name: "Phaktanlung Rural Municipality", type: "RM", district: "TAP", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10102", mofaga: "10102", name: "Mikwakhola Rural Municipality", type: "RM", district: "TAP", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10103", mofaga: "10103", name: "Meringden Rural Municipality", type: "RM", district: "TAP", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10104", mofaga: "10104", name: "Maiwakhola Rural Municipality", type: "RM", district: "TAP", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10105", mofaga: "10105", name: "Aatharai Tribeni Rural Municipality", type: "RM", district: "TAP", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10106", mofaga: "10106", name: "Phungling Municipality", type: "M", district: "TAP", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10107", mofaga: "10107", name: "Yangwarak Rural Municipality", type: "RM", district: "TAP", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10108", mofaga: "10108", name: "Sirijanga Rural Municipality", type: "RM", district: "TAP", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10109", mofaga: "10109", name: "Sidingba Rural Municipality", type: "RM", district: "TAP", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10201", mofaga: "10201", name: "Bhotkhola Rural Municipality", type: "RM", district: "SAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10202", mofaga: "10202", name: "Makalu Rural Municipality", type: "RM", district: "SAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10203", mofaga: "10203", name: "Silichong Rural Municipality", type: "RM", district: "SAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10204", mofaga: "10204", name: "Chichila Rural Municipality", type: "RM", district: "SAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10205", mofaga: "10205", name: "Sabhapokhari Rural Municipality", type: "RM", district: "SAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10206", mofaga: "10206", name: "Khandabari Municipality", type: "M", district: "SAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10207", mofaga: "10207", name: "Panchakhapan Municipality", type: "M", district: "SAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10208", mofaga: "10208", name: "Chainapur Municipality", type: "M", district: "SAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10209", mofaga: "10209", name: "Madi Municipality", type: "M", district: "SAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10210", mofaga: "10210", name: "Dharmadevi Municipality", type: "M", district: "SAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10301", mofaga: "10301", name: "Khumbu Pasanglhamu Rural Municipality", type: "RM", district: "SOL", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10302", mofaga: "10302", name: "Mahakulung Rural Municipality", type: "RM", district: "SOL", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10303", mofaga: "10303", name: "Sotang Rural Municipality", type: "RM", district: "SOL", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10304", mofaga: "10304", name: "Mapya Dudhkoshi Rural Municipality", type: "RM", district: "SOL", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10305", mofaga: "10305", name: "Thulung Dudhkoushi Rural Municipality", type: "RM", district: "SOL", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10306", mofaga: "10306", name: "Necha Salyan Rural Municipality", type: "RM", district: "SOL", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10307", mofaga: "10307", name: "Solu Dudhakunda Municipality", type: "M", district: "SOL", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10308", mofaga: "10308", name: "Likhu Pike Rural Municipality", type: "RM", district: "SOL", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10401", mofaga: "10401", name: "Chishankhu Gadhi Rural Municipality", type: "RM", district: "OKH", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10402", mofaga: "10402", name: "Siddhicharan Municipality", type: "M", district: "OKH", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10403", mofaga: "10403", name: "Molung Rural Municipality", type: "RM", district: "OKH", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10404", mofaga: "10404", name: "Khiji Demba Rural Municipality", type: "RM", district: "OKH", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10405", mofaga: "10405", name: "Likhu Rural Municipality", type: "RM", district: "OKH", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10406", mofaga: "10406", name: "Champadevi Rural Municipality", type: "RM", district: "OKH", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10407", mofaga: "10407", name: "Sunkoshi Rural Municipality", type: "RM", district: "OKH", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10408", mofaga: "10408", name: "Manebhanjyang Rural Municipality", type: "RM", district: "OKH", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10501", mofaga: "10501", name: "Kepilasgadhi Rural Municipality", type: "RM", district: "KHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10502", mofaga: "10502", name: "Aiselukharka Rural Municipality", type: "RM", district: "KHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10503", mofaga: "10503", name: "Rawabesi Rural Municipality", type: "RM", district: "KHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10504", mofaga: "10504", name: "Halesi Tuwachung Municipality", type: "M", district: "KHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10505", mofaga: "10505", name: "Diktel Rupakot Majhuwagadhi Municipality", type: "M", district: "KHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10506", mofaga: "10506", name: "Sakela Rural Municipality", type: "RM", district: "KHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10507", mofaga: "10507", name: "Diprung Rural Municipality", type: "RM", district: "KHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10508", mofaga: "10508", name: "Khotehang Rural Municipality", type: "RM", district: "KHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10509", mofaga: "10509", name: "Jante Dhunga Rural Municipality", type: "RM", district: "KHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10510", mofaga: "10510", name: "Baraha Pokhari Rural Municipality", type: "RM", district: "KHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10601", mofaga: "10601", name: "Shadananda Municipality", type: "M", district: "BHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10602", mofaga: "10602", name: "Salpa Silichho Rural Municipality", type: "RM", district: "BHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10603", mofaga: "10603", name: "Tyamke Maiyum Rural Municipality", type: "RM", district: "BHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10604", mofaga: "10604", name: "Bhojpur Municipality", type: "M", district: "BHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10605", mofaga: "10605", name: "Arun Rural Municipality", type: "RM", district: "BHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10606", mofaga: "10606", name: "Pauwa Dunma Rural Municipality", type: "RM", district: "BHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10607", mofaga: "10607", name: "Ramprasad Rai Rural Municipality", type: "RM", district: "BHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10608", mofaga: "10608", name: "Hatuwagadhi Rural Municipality", type: "RM", district: "BHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10609", mofaga: "10609", name: "Aamchowk Rural Municipality", type: "RM", district: "BHO", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10701", mofaga: "10701", name: "Mahalaxmi Municipality", type: "M", district: "DHAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10702", mofaga: "10702", name: "Pakhribas Municipality", type: "M", district: "DHAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10703", mofaga: "10703", name: "Chhathar Jorpati Rural Municipality", type: "RM", district: "DHAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10704", mofaga: "10704", name: "Dhankuta Municipality", type: "M", district: "DHAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10705", mofaga: "10705", name: "Sahidbhumi Rural Municipality", type: "RM", district: "DHAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10706", mofaga: "10706", name: "Sangurigadhi Rural Municipality", type: "RM", district: "DHAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10707", mofaga: "10707", name: "Chaubise Rural Municipality", type: "RM", district: "DHAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10801", mofaga: "10801", name: "Aatharai Rural Municipality", type: "RM", district: "TER", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10802", mofaga: "10802", name: "Phedap Rural Municipality", type: "RM", district: "TER", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10803", mofaga: "10803", name: "Menchhayayem Rural Municipality", type: "RM", district: "TER", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10804", mofaga: "10804", name: "Myanglung Municipality", type: "M", district: "TER", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10805", mofaga: "10805", name: "Laligurans Municipality", type: "M", district: "TER", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10806", mofaga: "10806", name: "Chhathar Rural Municipality", type: "RM", district: "TER", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10901", mofaga: "10901", name: "Yangbarak Rural Municipality", type: "RM", district: "PAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10902", mofaga: "10902", name: "Hilihan Rural Municipality", type: "RM", district: "PAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10903", mofaga: "10903", name: "Falelung Rural Municipality", type: "RM", district: "PAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10904", mofaga: "10904", name: "Phidim Municipality", type: "M", district: "PAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10905", mofaga: "10905", name: "Falgunanda Rural Municipality", type: "RM", district: "PAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10906", mofaga: "10906", name: "Kummayak Rural Municipality", type: "RM", district: "PAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10907", mofaga: "10907", name: "Tumbewa Rural Municipality", type: "RM", district: "PAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF10908", mofaga: "10908", name: "Miklajung Rural Municipality", type: "RM", district: "PAN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11001", mofaga: "11001", name: "Mai Jogmai Rural Municipality", type: "RM", district: "ILA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11002", mofaga: "11002", name: "Sandakpur Rural Municipality", type: "RM", district: "ILA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11003", mofaga: "11003", name: "Ilam Municipality", type: "M", district: "ILA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11004", mofaga: "11004", name: "Deumai Municipality", type: "M", district: "ILA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11005", mofaga: "11005", name: "Fakfokathum Rural Municipality", type: "RM", district: "ILA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11006", mofaga: "11006", name: "Mangsebung Rural Municipality", type: "RM", district: "ILA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11007", mofaga: "11007", name: "Chulachuli Rural Municipality", type: "RM", district: "ILA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11008", mofaga: "11008", name: "Mai Municipality", type: "M", district: "ILA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11009", mofaga: "11009", name: "Suryodaya Municipality", type: "M", district: "ILA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11010", mofaga: "11010", name: "Rong Rural Municipality", type: "RM", district: "ILA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11101", mofaga: "11101", name: "Mechinagar Municipality", type: "M", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11102", mofaga: "11102", name: "Buddhashanti Rural Municipality", type: "RM", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11103", mofaga: "11103", name: "Arjundhara Municipality", type: "M", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11104", mofaga: "11104", name: "Kankai Municipality", type: "M", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11105", mofaga: "11105", name: "Shivasatakshi Municipality", type: "M", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11106", mofaga: "11106", name: "Kamal Rural Municipality", type: "RM", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11107", mofaga: "11107", name: "Damak Municipality", type: "M", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11108", mofaga: "11108", name: "Gauradaha Municipality", type: "M", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11109", mofaga: "11109", name: "Gauriganj Rural Municipality", type: "RM", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11110", mofaga: "11110", name: "Jhapa Rural Municipality", type: "RM", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11111", mofaga: "11111", name: "Barhadashi Rural Municipality", type: "RM", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11112", mofaga: "11112", name: "Birtamod Municipality", type: "M", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11113", mofaga: "11113", name: "Haldibari Rural Municipality", type: "RM", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11114", mofaga: "11114", name: "Bhadrapur Municipality", type: "M", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11115", mofaga: "11115", name: "Kachanakawal Rural Municipality", type: "RM", district: "JHA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11201", mofaga: "11201", name: "Miklajung Rural Municipality", type: "RM", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11202", mofaga: "11202", name: "Letang Municipality", type: "M", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11203", mofaga: "11203", name: "Kerabari Rural Municipality", type: "RM", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11204", mofaga: "11204", name: "Sundarharaicha Municipality", type: "M", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11205", mofaga: "11205", name: "Belbari Municipality", type: "M", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11206", mofaga: "11206", name: "Kanepokhari Rural Municipality", type: "RM", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11207", mofaga: "11207", name: "Pathari Shanishchare Municipality", type: "M", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11208", mofaga: "11208", name: "Urlabari Municipality", type: "M", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11209", mofaga: "11209", name: "Ratuwamai Municipality", type: "M", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11210", mofaga: "11210", name: "Sunwarshi Municipality", type: "M", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11211", mofaga: "11211", name: "Rangeli Municipality", type: "M", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11212", mofaga: "11212", name: "Gramthan Rural Municipality", type: "RM", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11213", mofaga: "11213", name: "Budhiganga Rural Municipality", type: "RM", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11214", mofaga: "11214", name: "Biratnagar Metropolitan City", type: "MC", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11215", mofaga: "11215", name: "Katahari Rural Municipality", type: "RM", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11216", mofaga: "11216", name: "Dhanapalthan Rural Municipality", type: "RM", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11217", mofaga: "11217", name: "Jahada Rural Municipality", type: "RM", district: "MOR", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11301", mofaga: "11301", name: "Dharan Sub-Metropolitan City", type: "SMC", district: "SUN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11302", mofaga: "11302", name: "Baraha Municipality", type: "M", district: "SUN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11303", mofaga: "11303", name: "Koshi Rural Municipality", type: "RM", district: "SUN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11304", mofaga: "11304", name: "Bhokraha Rural Municipality", type: "RM", district: "SUN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11305", mofaga: "11305", name: "Ramdhuni Municipality", type: "M", district: "SUN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11306", mofaga: "11306", name: "Itahari Sub-Metropolitan City", type: "SMC", district: "SUN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11307", mofaga: "11307", name: "Duhabi Municipality", type: "M", district: "SUN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11308", mofaga: "11308", name: "Gadhi Rural Municipality", type: "RM", district: "SUN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11309", mofaga: "11309", name: "Inaruwa Municipality", type: "M", district: "SUN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11310", mofaga: "11310", name: "Harinagara Rural Municipality", type: "RM", district: "SUN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11311", mofaga: "11311", name: "Dewangunj Rural Municipality", type: "RM", district: "SUN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11312", mofaga: "11312", name: "Barju Rural Municipality", type: "RM", district: "SUN", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11401", mofaga: "11401", name: "Belaka Municipality", type: "M", district: "UDA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11402", mofaga: "11402", name: "Chaudandigadhi Municipality", type: "M", district: "UDA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11403", mofaga: "11403", name: "Triyuga Municipality", type: "M", district: "UDA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11404", mofaga: "11404", name: "Rautamai Rural Municipality", type: "RM", district: "UDA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11405", mofaga: "11405", name: "Sunkoshi Rural Municipality", type: "RM", district: "UDA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11406", mofaga: "11406", name: "Tapli Rural Municipality", type: "RM", district: "UDA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11407", mofaga: "11407", name: "Katari Municipality", type: "M", district: "UDA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF11408", mofaga: "11408", name: "Udayapurgadhi Rural Municipality", type: "RM", district: "UDA", province: "Koshi", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20101", mofaga: "20101", name: "Saptakoshi Municipality", type: "M", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20102", mofaga: "20102", name: "Kanchanrup Municipality", type: "M", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20103", mofaga: "20103", name: "Agnisair Krishna Sabaran Rural Municipality", type: "RM", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20104", mofaga: "20104", name: "Rupani Rural Municipality", type: "RM", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20105", mofaga: "20105", name: "Shambhunath Municipality", type: "M", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20106", mofaga: "20106", name: "Khadak Municipality", type: "M", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20107", mofaga: "20107", name: "Surunga Municipality", type: "M", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20108", mofaga: "20108", name: "Balan-Bihul Rural Municipality", type: "RM", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20109", mofaga: "20109", name: "BodeBarsain Municipality", type: "M", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20110", mofaga: "20110", name: "Dakneshwori Municipality", type: "M", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20111", mofaga: "20111", name: "Belhi Chapena Rural Municipality", type: "RM", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20112", mofaga: "20112", name: "Bishnupur Rural Municipality", type: "RM", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20113", mofaga: "20113", name: "Rajbiraj Municipality", type: "M", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20114", mofaga: "20114", name: "Mahadewa Rural Municipality", type: "RM", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20115", mofaga: "20115", name: "Tirahut Rural Municipality", type: "RM", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20116", mofaga: "20116", name: "Hanumannagar Kankalini Municipality", type: "M", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20117", mofaga: "20117", name: "Tilathi Koiladi Rural Municipality", type: "RM", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20118", mofaga: "20118", name: "Chhinnamasta Rural Municipality", type: "RM", district: "SAP", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20201", mofaga: "20201", name: "Lahan Municipality", type: "M", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20202", mofaga: "20202", name: "Dhangadhimai Municipality", type: "M", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20203", mofaga: "20203", name: "Golbazar Municipality", type: "M", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20204", mofaga: "20204", name: "Mirchaiya Municipality", type: "M", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20205", mofaga: "20205", name: "Karjanha Municipality", type: "M", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20206", mofaga: "20206", name: "Kalyanpur Municipality", type: "M", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20207", mofaga: "20207", name: "Naraha Rural Municipality", type: "RM", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20208", mofaga: "20208", name: "Bishnupur Rural Municipality", type: "RM", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20209", mofaga: "20209", name: "Arnama Rural Municipality", type: "RM", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20210", mofaga: "20210", name: "Sukhipur Municipality", type: "M", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20211", mofaga: "20211", name: "Laxmipur Patari Rural Municipality", type: "RM", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20212", mofaga: "20212", name: "Sakhuwa Nankarkatti Rural Municipality", type: "RM", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20213", mofaga: "20213", name: "Bhagawanpur Rural Municipality", type: "RM", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20214", mofaga: "20214", name: "Nawarajpur Rural Municipality", type: "RM", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20215", mofaga: "20215", name: "Bariyarpatti Rural Municipality", type: "RM", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20216", mofaga: "20216", name: "Aurahi Rural Municipality", type: "RM", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20217", mofaga: "20217", name: "Siraha Municipality", type: "M", district: "SIR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20301", mofaga: "20301", name: "Ganeshman Charnath Municipality", type: "M", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20302", mofaga: "20302", name: "Dhanushadham Municipality", type: "M", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20303", mofaga: "20303", name: "Mithila Municipality", type: "M", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20304", mofaga: "20304", name: "Bateshwor Rural Municipality", type: "RM", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20305", mofaga: "20305", name: "Chhireshwornath Municipality", type: "M", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20306", mofaga: "20306", name: "Laxminiya Rural Municipality", type: "RM", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20307", mofaga: "20307", name: "Mithila Bihari Municipality", type: "M", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20308", mofaga: "20308", name: "Hansapur Municipality", type: "M", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20309", mofaga: "20309", name: "Sabaila Municipality", type: "M", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20310", mofaga: "20310", name: "Shahidnagar Municipality", type: "M", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20311", mofaga: "20311", name: "Kamala Municipality", type: "M", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20312", mofaga: "20312", name: "Janak Nandini Rural Municipality", type: "RM", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20313", mofaga: "20313", name: "Bideha Municipality", type: "M", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20314", mofaga: "20314", name: "Aurahi Rural Municipality", type: "RM", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20315", mofaga: "20315", name: "Janakpur Sub-Metropolitan City", type: "SMC", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20316", mofaga: "20316", name: "Dhanauji Rural Municipality", type: "RM", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20317", mofaga: "20317", name: "Nagarain Municipality", type: "M", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20318", mofaga: "20318", name: "Mukhiyapatti Musaharmiya Rural Municipality", type: "RM", district: "DHAN", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20401", mofaga: "20401", name: "Bardibas Municipality", type: "M", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20402", mofaga: "20402", name: "Gaushala Municipality", type: "M", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20403", mofaga: "20403", name: "Sonama Rural Municipality", type: "RM", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20404", mofaga: "20404", name: "Aurahi Municipality", type: "M", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20405", mofaga: "20405", name: "Bhangaha Municipality", type: "M", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20406", mofaga: "20406", name: "Loharpatti Municipality", type: "M", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20407", mofaga: "20407", name: "Balawa Municipality", type: "M", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20408", mofaga: "20408", name: "Ram Gopalpur Municipality", type: "M", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20409", mofaga: "20409", name: "Samsi Rural Municipality", type: "RM", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20410", mofaga: "20410", name: "Manara Shisawa Municipality", type: "M", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20411", mofaga: "20411", name: "Ekadara Rural Municipality", type: "RM", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20412", mofaga: "20412", name: "Mahottari Rural Municipality", type: "RM", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20413", mofaga: "20413", name: "Pipara Rural Municipality", type: "RM", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20414", mofaga: "20414", name: "Matihani Municipality", type: "M", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20415", mofaga: "20415", name: "Jaleshwor Municipality", type: "M", district: "MAH", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20501", mofaga: "20501", name: "Lalbandi Municipality", type: "M", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20502", mofaga: "20502", name: "Hariwan Municipality", type: "M", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20503", mofaga: "20503", name: "Bagmati Municipality", type: "M", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20504", mofaga: "20504", name: "Barahathawa Municipality", type: "M", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20505", mofaga: "20505", name: "Haripur Municipality", type: "M", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20506", mofaga: "20506", name: "Ishworpur Municipality", type: "M", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20507", mofaga: "20507", name: "Haripurwa Municipality", type: "M", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20508", mofaga: "20508", name: "Parsa Rural Municipality", type: "RM", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20509", mofaga: "20509", name: "Brahmapuri Rural Municipality", type: "RM", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20510", mofaga: "20510", name: "Chandranagar Rural Municipality", type: "RM", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20511", mofaga: "20511", name: "Kabilashi Municipality", type: "M", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20512", mofaga: "20512", name: "Chakraghatta Rural Municipality", type: "RM", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20513", mofaga: "20513", name: "Basbariya Rural Municipality", type: "RM", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20514", mofaga: "20514", name: "Dhanakaul Rural Municipality", type: "RM", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20515", mofaga: "20515", name: "Ramnagar Rural Municipality", type: "RM", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20516", mofaga: "20516", name: "Balara Municipality", type: "M", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20517", mofaga: "20517", name: "Godaita Municipality", type: "M", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20518", mofaga: "20518", name: "Bishnu Rural Municipality", type: "RM", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20519", mofaga: "20519", name: "Kaudena Rural Municipality", type: "RM", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20520", mofaga: "20520", name: "Malangawa Municipality", type: "M", district: "SAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20601", mofaga: "20601", name: "Chandrapur Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20602", mofaga: "20602", name: "Gujara Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20603", mofaga: "20603", name: "Phatuwa Bijayapur Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20604", mofaga: "20604", name: "Katahariya Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20605", mofaga: "20605", name: "Brindaban Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20606", mofaga: "20606", name: "Gadhimai Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20607", mofaga: "20607", name: "Madhav Narayan Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20608", mofaga: "20608", name: "Garuda Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20609", mofaga: "20609", name: "Dewahi Gonahi Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20610", mofaga: "20610", name: "Maulapur Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20611", mofaga: "20611", name: "Boudhimai Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20612", mofaga: "20612", name: "Paroha Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20613", mofaga: "20613", name: "Rajpur Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20614", mofaga: "20614", name: "Yamunamai Rural Municipality", type: "RM", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20615", mofaga: "20615", name: "Durga Bhagawati Rural Municipality", type: "RM", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20616", mofaga: "20616", name: "Rajdevi Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20617", mofaga: "20617", name: "Gaur Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20618", mofaga: "20618", name: "Ishanath Municipality", type: "M", district: "RAU", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20701", mofaga: "20701", name: "Nijagadh Municipality", type: "M", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20702", mofaga: "20702", name: "Kolhabi Municipality", type: "M", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20703", mofaga: "20703", name: "Jitpur Simara Sub-Metropolitan City", type: "SMC", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20704", mofaga: "20704", name: "Parawanipur Rural Municipality", type: "RM", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20705", mofaga: "20705", name: "Prasauni Rural Municipality", type: "RM", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20706", mofaga: "20706", name: "Bishrampur Rural Municipality", type: "RM", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20707", mofaga: "20707", name: "Pheta Rural Municipality", type: "RM", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20708", mofaga: "20708", name: "Kalaiya Sub-Metropolitan City", type: "SMC", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20709", mofaga: "20709", name: "Karaiyamai Rural Municipality", type: "RM", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20710", mofaga: "20710", name: "Baragadhi Rural Municipality", type: "RM", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20711", mofaga: "20711", name: "Aadarsha Kotwal Rural Municipality", type: "RM", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20712", mofaga: "20712", name: "Simroungadh Municipality", type: "M", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20713", mofaga: "20713", name: "Pacharauta Municipality", type: "M", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20714", mofaga: "20714", name: "Mahagadhimai Municipality", type: "M", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20715", mofaga: "20715", name: "Devtal Rural Municipality", type: "RM", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20716", mofaga: "20716", name: "Subarna Rural Municipality", type: "RM", district: "BAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20801", mofaga: "20801", name: "Thori Rural Municipality", type: "RM", district: "PAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20802", mofaga: "20802", name: "Jirabhawani Rural Municipality", type: "RM", district: "PAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20803", mofaga: "20803", name: "Jagarnathpur Rural Municipality", type: "RM", district: "PAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20804", mofaga: "20804", name: "Paterwa Sugauli Rural Municipality", type: "RM", district: "PAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20805", mofaga: "20805", name: "Sakhuwa Prasauni Rural Municipality", type: "RM", district: "PAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20806", mofaga: "20806", name: "Parsagadhi Municipality", type: "M", district: "PAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20807", mofaga: "20807", name: "Birgunj Metropolitan City", type: "MC", district: "PAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20808", mofaga: "20808", name: "Bahudarmai Municipality", type: "M", district: "PAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20809", mofaga: "20809", name: "Pokhariya Municipality", type: "M", district: "PAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20810", mofaga: "20810", name: "Kalikamai Rural Municipality", type: "RM", district: "PAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20811", mofaga: "20811", name: "Dhobini Rural Municipality", type: "RM", district: "PAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20812", mofaga: "20812", name: "Chhipaharmai Rural Municipality", type: "RM", district: "PAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20813", mofaga: "20813", name: "Pakaha Mainpur Rural Municipality", type: "RM", district: "PAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF20814", mofaga: "20814", name: "Bindabasini Rural Municipality", type: "RM", district: "PAR", province: "Madhesh", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30101", mofaga: "30101", name: "Gaurishankar Rural Municipality", type: "RM", district: "DOL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30102", mofaga: "30102", name: "Bigu Rural Municipality", type: "RM", district: "DOL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30103", mofaga: "30103", name: "Kalinchowk Rural Municipality", type: "RM", district: "DOL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30104", mofaga: "30104", name: "Baitedhar Rural Municipality", type: "RM", district: "DOL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30105", mofaga: "30105", name: "Jiri Municipality", type: "M", district: "DOL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30106", mofaga: "30106", name: "Tamakoshi Rural Municipality", type: "RM", district: "DOL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30107", mofaga: "30107", name: "Melung Rural Municipality", type: "RM", district: "DOL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30108", mofaga: "30108", name: "Shailung Rural Municipality", type: "RM", district: "DOL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30109", mofaga: "30109", name: "Bhimeshwor Municipality", type: "M", district: "DOL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30201", mofaga: "30201", name: "Bhotekoshi Rural Municipality", type: "RM", district: "SIN", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30202", mofaga: "30202", name: "Jugal Rural Municipality", type: "RM", district: "SIN", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30203", mofaga: "30203", name: "Panchpokhari Thangpal Rural Municipality", type: "RM", district: "SIN", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30204", mofaga: "30204", name: "Helambu Rural Municipality", type: "RM", district: "SIN", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30205", mofaga: "30205", name: "Melamchi Municipality", type: "M", district: "SIN", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30206", mofaga: "30206", name: "Indrawoti Rural Municipality", type: "RM", district: "SIN", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30208", mofaga: "30208", name: "Balephi Rural Municipality", type: "RM", district: "SIN", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30209", mofaga: "30209", name: "Bahrabise Municipality", type: "M", district: "SIN", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30210", mofaga: "30210", name: "Tripurasundari Rural Municipality", type: "RM", district: "SIN", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30211", mofaga: "30211", name: "Lisankhu Pakhar Rural Municipality", type: "RM", district: "SIN", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30212", mofaga: "30212", name: "Sunkoshi Rural Municipality", type: "RM", district: "SIN", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30305", mofaga: "30305", name: "Naukunda Rural Municipality", type: "RM", district: "RAS", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30401", mofaga: "30401", name: "Rubi Valley Rural Municipality", type: "RM", district: "DHA", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30402", mofaga: "30402", name: "Khaniyabas Rural Municipality", type: "RM", district: "DHA", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30403", mofaga: "30403", name: "Ganga Jamuna Rural Municipality", type: "RM", district: "DHA", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30404", mofaga: "30404", name: "Tripurasundari Rural Municipality", type: "RM", district: "DHA", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30405", mofaga: "30405", name: "Netrawati Rural Municipality", type: "RM", district: "DHA", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30406", mofaga: "30406", name: "Nilkhantha Municipality", type: "M", district: "DHA", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30407", mofaga: "30407", name: "Jwalamukhi Rural Municipality", type: "RM", district: "DHA", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30412", mofaga: "30412", name: "Thakre Rural Municipality", type: "RM", district: "DHA", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30413", mofaga: "30413", name: "Dhunibenshi Municipality", type: "M", district: "DHA", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30501", mofaga: "30501", name: "Dupcheshwor Rural Municipality", type: "RM", district: "NUW", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30502", mofaga: "30502", name: "Tadi Rural Municipality", type: "RM", district: "NUW", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30503", mofaga: "30503", name: "Suryagadhi Rural Municipality", type: "RM", district: "NUW", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30506", mofaga: "30506", name: "Meghang Rural Municipality", type: "RM", district: "NUW", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30510", mofaga: "30510", name: "Panchakanya Rural Municipality", type: "RM", district: "NUW", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30511", mofaga: "30511", name: "Shivapuri Rural Municipality", type: "RM", district: "NUW", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30512", mofaga: "30512", name: "Kakani Rural Municipality", type: "RM", district: "NUW", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30601", mofaga: "30601", name: "Shankharapur Municipality", type: "M", district: "KTM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30602", mofaga: "30602", name: "Kageshwori Manahara Municipality", type: "M", district: "KTM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30603", mofaga: "30603", name: "Gokarneshwor Municipality", type: "M", district: "KTM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30604", mofaga: "30604", name: "Budhanilkhantha Municipality", type: "M", district: "KTM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30605", mofaga: "30605", name: "Tokha Municipality", type: "M", district: "KTM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30606", mofaga: "30606", name: "Tarakeshwor Municipality", type: "M", district: "KTM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30607", mofaga: "30607", name: "Nagarjun Municipality", type: "M", district: "KTM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30609", mofaga: "30609", name: "Kirtipur Municipality", type: "M", district: "KTM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30610", mofaga: "30610", name: "Chandragiri Municipality", type: "M", district: "KTM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30611", mofaga: "30611", name: "Dakshinkali Municipality", type: "M", district: "KTM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30701", mofaga: "30701", name: "Changunarayan Municipality", type: "M", district: "BHA", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30702", mofaga: "30702", name: "Bhaktapur Municipality", type: "M", district: "BHA", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30703", mofaga: "30703", name: "Madhyapur Thimi Municipality", type: "M", district: "BHA", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30704", mofaga: "30704", name: "Suryabinayak Municipality", type: "M", district: "BHA", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30801", mofaga: "30801", name: "Mahalaxmi Municipality", type: "M", district: "LAL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30802", mofaga: "30802", name: "Lalitpur Metropolitan City", type: "MC", district: "LAL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30803", mofaga: "30803", name: "Godawari Municipality", type: "M", district: "LAL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30804", mofaga: "30804", name: "Konjyosom Rural Municipality", type: "RM", district: "LAL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30805", mofaga: "30805", name: "Mahankal Rural Municipality", type: "RM", district: "LAL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30806", mofaga: "30806", name: "Bagmati Rural Municipality", type: "RM", district: "LAL", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30901", mofaga: "30901", name: "Chauri Deurali Rural Municipality", type: "RM", district: "KAV", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30902", mofaga: "30902", name: "Bhumlu Rural Municipality", type: "RM", district: "KAV", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30903", mofaga: "30903", name: "Mandan Deupur Municipality", type: "M", district: "KAV", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30904", mofaga: "30904", name: "Banepa Municipality", type: "M", district: "KAV", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30905", mofaga: "30905", name: "Dhulikhel Municipality", type: "M", district: "KAV", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30906", mofaga: "30906", name: "Panchkhal Municipality", type: "M", district: "KAV", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30907", mofaga: "30907", name: "Temal Rural Municipality", type: "RM", district: "KAV", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30908", mofaga: "30908", name: "Namobuddha Municipality", type: "M", district: "KAV", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30909", mofaga: "30909", name: "Panauti Municipality", type: "M", district: "KAV", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30910", mofaga: "30910", name: "Bethanchowk Rural Municipality", type: "RM", district: "KAV", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30911", mofaga: "30911", name: "Roshi Rural Municipality", type: "RM", district: "KAV", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30912", mofaga: "30912", name: "Mahabharat Rural Municipality", type: "RM", district: "KAV", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF30913", mofaga: "30913", name: "Khanikhola Rural Municipality", type: "RM", district: "KAV", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31001", mofaga: "31001", name: "Umakunda Rural Municipality", type: "RM", district: "RAM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31002", mofaga: "31002", name: "Gokulganga Rural Municipality", type: "RM", district: "RAM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31003", mofaga: "31003", name: "Likhu Rural Municipality", type: "RM", district: "RAM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31004", mofaga: "31004", name: "Ramechhap Municipality", type: "M", district: "RAM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31005", mofaga: "31005", name: "Manthali Municipality", type: "M", district: "RAM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31006", mofaga: "31006", name: "Khandadevi Rural Municipality", type: "RM", district: "RAM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31007", mofaga: "31007", name: "Doramba Rural Municipality", type: "RM", district: "RAM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31008", mofaga: "31008", name: "Sunapati Rural Municipality", type: "RM", district: "RAM", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31101", mofaga: "31101", name: "Dudhouli Municipality", type: "M", district: "SIND", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31102", mofaga: "31102", name: "Phikkal Rural Municipality", type: "RM", district: "SIND", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31103", mofaga: "31103", name: "Tinpatan Rural Municipality", type: "RM", district: "SIND", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31104", mofaga: "31104", name: "Golanjor Rural Municipality", type: "RM", district: "SIND", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31105", mofaga: "31105", name: "Kamalamai Municipality", type: "M", district: "SIND", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31106", mofaga: "31106", name: "Sunkoshi Rural Municipality", type: "RM", district: "SIND", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31107", mofaga: "31107", name: "Ghyanglekha Rural Municipality", type: "RM", district: "SIND", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31108", mofaga: "31108", name: "Marin Rural Municipality", type: "RM", district: "SIND", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31109", mofaga: "31109", name: "Hariharpurgaghi Rural Municipality", type: "RM", district: "SIND", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31201", mofaga: "31201", name: "Indrasarowar Rural Municipality", type: "RM", district: "MAK", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31202", mofaga: "31202", name: "Thaha Municipality", type: "M", district: "MAK", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31203", mofaga: "31203", name: "Kailash Rural Municipality", type: "RM", district: "MAK", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31204", mofaga: "31204", name: "Raksirang Rural Municipality", type: "RM", district: "MAK", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31205", mofaga: "31205", name: "Manahari Rural Municipality", type: "RM", district: "MAK", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31206", mofaga: "31206", name: "Hetauda Sub-Metropolitan City", type: "SMC", district: "MAK", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31207", mofaga: "31207", name: "Bhimphedi Rural Municipality", type: "RM", district: "MAK", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31208", mofaga: "31208", name: "Makawanpurgadhi Rural Municipality", type: "RM", district: "MAK", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31209", mofaga: "31209", name: "Bakaiya Rural Municipality", type: "RM", district: "MAK", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31210", mofaga: "31210", name: "Bagmati Rural Municipality", type: "RM", district: "MAK", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31301", mofaga: "31301", name: "Rapti Municipality", type: "M", district: "CHT", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31302", mofaga: "31302", name: "Kalika Municipality", type: "M", district: "CHT", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31305", mofaga: "31305", name: "Ratnanagar Municipality", type: "M", district: "CHT", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31306", mofaga: "31306", name: "Khairahani Municipality", type: "M", district: "CHT", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF31307", mofaga: "31307", name: "Madi Municipality", type: "M", district: "CHT", province: "Bagmati", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40101", mofaga: "40101", name: "Chumanubri Rural Municipality", type: "RM", district: "GOR", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40102", mofaga: "40102", name: "Ajirkot Rural Municipality", type: "RM", district: "GOR", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40103", mofaga: "40103", name: "Sulikot Rural Municipality", type: "RM", district: "GOR", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40104", mofaga: "40104", name: "Dharche Rural Municipality", type: "RM", district: "GOR", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40105", mofaga: "40105", name: "Aarughat Rural Municipality", type: "RM", district: "GOR", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40106", mofaga: "40106", name: "Bhimsen Rural Municipality", type: "RM", district: "GOR", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40107", mofaga: "40107", name: "Siranchowk Rural Municipality", type: "RM", district: "GOR", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40108", mofaga: "40108", name: "Palungtar Municipality", type: "M", district: "GOR", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40109", mofaga: "40109", name: "Gorkha Municipality", type: "M", district: "GOR", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40201", mofaga: "40201", name: "Naraphu Rural Municipality", type: "RM", district: "MAN", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40202", mofaga: "40202", name: "Neshang Rural Municipality", type: "RM", district: "MAN", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40203", mofaga: "40203", name: "Chame Rural Municipality", type: "RM", district: "MAN", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40204", mofaga: "40204", name: "Nashong Rural Municipality", type: "RM", district: "MAN", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40301", mofaga: "40301", name: "Dalome Rural Municipality", type: "RM", district: "MUS", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40302", mofaga: "40302", name: "Gharpajhong Rural Municipality", type: "RM", district: "MUS", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40303", mofaga: "40303", name: "Bahragaun Muktikshetra Rural Municipality", type: "RM", district: "MUS", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40304", mofaga: "40304", name: "Lomanthang Rural Municipality", type: "RM", district: "MUS", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40305", mofaga: "40305", name: "Thasang Rural Municipality", type: "RM", district: "MUS", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40401", mofaga: "40401", name: "Annapurna Rural Municipality", type: "RM", district: "MYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40402", mofaga: "40402", name: "Raghuganga Rural Municipality", type: "RM", district: "MYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40403", mofaga: "40403", name: "Dhawalagiri Rural Municipality", type: "RM", district: "MYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40404", mofaga: "40404", name: "Malika Rural Municipality", type: "RM", district: "MYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40405", mofaga: "40405", name: "Mangala Rural Municipality", type: "RM", district: "MYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40406", mofaga: "40406", name: "Beni Municipality", type: "M", district: "MYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40501", mofaga: "40501", name: "Madi Rural Municipality", type: "RM", district: "KAS", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40502", mofaga: "40502", name: "Machhapuchchhre Rural Municipality", type: "RM", district: "KAS", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40503", mofaga: "40503", name: "Annapurna Rural Municipality", type: "RM", district: "KAS", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40504", mofaga: "40504", name: "Pokhara Lekhnath Metropolitan City", type: "MC", district: "KAS", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40505", mofaga: "40505", name: "Rupa Rural Municipality", type: "RM", district: "KAS", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40601", mofaga: "40601", name: "Dordi Rural Municipality", type: "RM", district: "LAM", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40602", mofaga: "40602", name: "Marshyangdi Rural Municipality", type: "RM", district: "LAM", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40603", mofaga: "40603", name: "Kwhola Sothar Rural Municipality", type: "RM", district: "LAM", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40604", mofaga: "40604", name: "Madhya Nepal Municipality", type: "M", district: "LAM", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40605", mofaga: "40605", name: "Bensi Shahar Municipality", type: "M", district: "LAM", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40606", mofaga: "40606", name: "Sundarbazar Municipality", type: "M", district: "LAM", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40607", mofaga: "40607", name: "Rainas Municipality", type: "M", district: "LAM", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40608", mofaga: "40608", name: "Dudhapokhari Rural Municipality", type: "RM", district: "LAM", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40701", mofaga: "40701", name: "Bhanu Municipality", type: "M", district: "TAN", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40702", mofaga: "40702", name: "Byas Municipality", type: "M", district: "TAN", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40703", mofaga: "40703", name: "Myagde Rural Municipality", type: "RM", district: "TAN", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40704", mofaga: "40704", name: "Shuklagandaki Municipality", type: "M", district: "TAN", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40705", mofaga: "40705", name: "Bhimad Municipality", type: "M", district: "TAN", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40706", mofaga: "40706", name: "Ghiring Rural Municipality", type: "RM", district: "TAN", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40707", mofaga: "40707", name: "Rhishing Rural Municipality", type: "RM", district: "TAN", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40708", mofaga: "40708", name: "Devghat Rural Municipality", type: "RM", district: "TAN", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40709", mofaga: "40709", name: "Bandipur Rural Municipality", type: "RM", district: "TAN", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40710", mofaga: "40710", name: "Aanbu Khaireni Rural Municipality", type: "RM", district: "TAN", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40801", mofaga: "40801", name: "Gaidakot Municipality", type: "M", district: "NAW", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40802", mofaga: "40802", name: "Bulingtar Rural Municipality", type: "RM", district: "NAW", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40803", mofaga: "40803", name: "Bungdikali Rural Municipality", type: "RM", district: "NAW", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40804", mofaga: "40804", name: "Hupsekot Rural Municipality", type: "RM", district: "NAW", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40805", mofaga: "40805", name: "Devchuli Municipality", type: "M", district: "NAW", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40806", mofaga: "40806", name: "Kawasoti Municipality", type: "M", district: "NAW", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40808", mofaga: "40808", name: "Binayi Tribeni Rural Municipality", type: "RM", district: "NAW", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40901", mofaga: "40901", name: "Putalibazar Municipality", type: "M", district: "SYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40902", mofaga: "40902", name: "Phedikhola Rural Municipality", type: "RM", district: "SYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40903", mofaga: "40903", name: "Aandhikhola Rural Municipality", type: "RM", district: "SYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40904", mofaga: "40904", name: "Arjun Choupari Rural Municipality", type: "RM", district: "SYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40905", mofaga: "40905", name: "Bhirkot Municipaity", type: "", district: "SYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40906", mofaga: "40906", name: "Biruwa Rural Municipality", type: "RM", district: "SYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40907", mofaga: "40907", name: "Harinas Rural Municipality", type: "RM", district: "SYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40908", mofaga: "40908", name: "Chapakot Municipality", type: "M", district: "SYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40909", mofaga: "40909", name: "Walling Municipality", type: "M", district: "SYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40910", mofaga: "40910", name: "Galyang Municipality", type: "M", district: "SYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF40911", mofaga: "40911", name: "Kaligandaki Rural Municipality", type: "RM", district: "SYA", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41001", mofaga: "41001", name: "Modi Rural Municipality", type: "RM", district: "PARB", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41002", mofaga: "41002", name: "Jaljala Rural Municipality", type: "RM", district: "PARB", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41003", mofaga: "41003", name: "Kushma Municipality", type: "M", district: "PARB", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41004", mofaga: "41004", name: "Phalebas Municipality", type: "M", district: "PARB", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41005", mofaga: "41005", name: "Mahashila Rural Municipality", type: "RM", district: "PARB", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41006", mofaga: "41006", name: "Bihadi Rural Municipality", type: "RM", district: "PARB", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41007", mofaga: "41007", name: "Paiyu Rural Municipality", type: "RM", district: "PARB", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41101", mofaga: "41101", name: "Baglung Municipality", type: "M", district: "BAG", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41102", mofaga: "41102", name: "Kathekhola Rural Municipality", type: "RM", district: "BAG", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41103", mofaga: "41103", name: "Tarakhola Rural Municipality", type: "RM", district: "BAG", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41104", mofaga: "41104", name: "Tamankhola Rural Municipality", type: "RM", district: "BAG", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41105", mofaga: "41105", name: "Dhorpatan Municipality", type: "M", district: "BAG", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41106", mofaga: "41106", name: "Nisikhola Rural Municipality", type: "RM", district: "BAG", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41107", mofaga: "41107", name: "Badigad Rural Municipality", type: "RM", district: "BAG", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41108", mofaga: "41108", name: "Galkot Municipality", type: "M", district: "BAG", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41109", mofaga: "41109", name: "Bareng Rural Municipality", type: "RM", district: "BAG", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF41110", mofaga: "41110", name: "Jaimuni Municipality", type: "M", district: "BAG", province: "Gandaki", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50101", mofaga: "50101", name: "Putha Uttanganga Rural Municipality", type: "RM", district: "RUK", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50102", mofaga: "50102", name: "Sisne Rural Municipality", type: "RM", district: "RUK", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50103", mofaga: "50103", name: "Bhoome Rural Municipality", type: "RM", district: "RUK", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50201", mofaga: "50201", name: "Sunchhahari Rural Municipality", type: "RM", district: "ROL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50202", mofaga: "50202", name: "Thabang Rural Municipality", type: "RM", district: "ROL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50203", mofaga: "50203", name: "Paribartan Rural Municipality", type: "RM", district: "ROL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50204", mofaga: "50204", name: "Gangadev Rural Municipality", type: "RM", district: "ROL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50205", mofaga: "50205", name: "Madi Rural Municipality", type: "RM", district: "ROL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50206", mofaga: "50206", name: "Tribeni Rural Municipality", type: "RM", district: "ROL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50207", mofaga: "50207", name: "Rolpa Municipality", type: "M", district: "ROL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50208", mofaga: "50208", name: "Runtigadhi Rural Municipality", type: "RM", district: "ROL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50209", mofaga: "50209", name: "Sunil Smriti Rural Municipality", type: "RM", district: "ROL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50210", mofaga: "50210", name: "Lungri Rural Municipality", type: "RM", district: "ROL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50301", mofaga: "50301", name: "Gaumukhi Rural Municipality", type: "RM", district: "PYU", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50302", mofaga: "50302", name: "Naubahini Rural Municipality", type: "RM", district: "PYU", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50303", mofaga: "50303", name: "Jhimaruk Rural Municipality", type: "RM", district: "PYU", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50304", mofaga: "50304", name: "Pyuthan Municipality", type: "M", district: "PYU", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50305", mofaga: "50305", name: "Sworgadwari Municipality", type: "M", district: "PYU", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50306", mofaga: "50306", name: "Mandavi Rural Municipality", type: "RM", district: "PYU", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50307", mofaga: "50307", name: "Mallarani Rural Municipality", type: "RM", district: "PYU", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50308", mofaga: "50308", name: "Aairawati Rural Municipality", type: "RM", district: "PYU", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50309", mofaga: "50309", name: "Sarumarani Rural Municipality", type: "RM", district: "PYU", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50401", mofaga: "50401", name: "Kali Gandaki Rural Municipality", type: "RM", district: "GUL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50402", mofaga: "50402", name: "Satyawoti Rural Municipality", type: "RM", district: "GUL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50403", mofaga: "50403", name: "Chandrakot Rural Municipality", type: "RM", district: "GUL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50404", mofaga: "50404", name: "Musikot Municipality", type: "M", district: "GUL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50405", mofaga: "50405", name: "Isma Rural Municipality", type: "RM", district: "GUL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50406", mofaga: "50406", name: "Malika Rural Municipality", type: "RM", district: "GUL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50407", mofaga: "50407", name: "Madane Rural Municipality", type: "RM", district: "GUL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50408", mofaga: "50408", name: "Dhurkot Rural Municipality", type: "RM", district: "GUL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50409", mofaga: "50409", name: "Resunga Municipality", type: "M", district: "GUL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50410", mofaga: "50410", name: "Gulmi Durbar Rural Municipality", type: "RM", district: "GUL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50411", mofaga: "50411", name: "Chhatrakot Rural Municipality", type: "RM", district: "GUL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50412", mofaga: "50412", name: "Ruru Rural Municipality", type: "RM", district: "GUL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50501", mofaga: "50501", name: "Chhatradev Rural Municipality", type: "RM", district: "ARG", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50502", mofaga: "50502", name: "Malarani Rural Municipality", type: "RM", district: "ARG", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50503", mofaga: "50503", name: "Bhumikasthan Municipality", type: "M", district: "ARG", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50504", mofaga: "50504", name: "Sandhikharka Municipality", type: "M", district: "ARG", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50505", mofaga: "50505", name: "Panini Rural Municipality", type: "RM", district: "ARG", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50506", mofaga: "50506", name: "Shitaganga Municipality", type: "M", district: "ARG", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50601", mofaga: "50601", name: "Rampur Municipality", type: "M", district: "PAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50602", mofaga: "50602", name: "Purbakhola Rural Municipality", type: "RM", district: "PAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50603", mofaga: "50603", name: "Rambha Rural Municipality", type: "RM", district: "PAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50604", mofaga: "50604", name: "Baganaskali Rural Municipality", type: "RM", district: "PAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50605", mofaga: "50605", name: "Tansen Municipality", type: "M", district: "PAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50606", mofaga: "50606", name: "Ribdikot Rural Municipality", type: "RM", district: "PAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50607", mofaga: "50607", name: "Rainadevi Chhahara Rural Municipality", type: "RM", district: "PAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50608", mofaga: "50608", name: "Tinau Rural Municipality", type: "RM", district: "PAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50609", mofaga: "50609", name: "Mathagadhi Rural Municipality", type: "RM", district: "PAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50610", mofaga: "50610", name: "Nisdi Rural Municipality", type: "RM", district: "PAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50701", mofaga: "50701", name: "Bardaghat Municipality", type: "M", district: "NAWAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50702", mofaga: "50702", name: "Sunawal Municipality", type: "M", district: "NAWAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50703", mofaga: "50703", name: "Ramgram Municipality", type: "M", district: "NAWAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50704", mofaga: "50704", name: "Palhinandan Rural Municipality", type: "RM", district: "NAWAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50705", mofaga: "50705", name: "Sarawal Rural Municipality", type: "RM", district: "NAWAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50706", mofaga: "50706", name: "Pratapapur Rural Municipality", type: "RM", district: "NAWAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50707", mofaga: "50707", name: "Susta Rural Municipality", type: "RM", district: "NAWAL", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50801", mofaga: "50801", name: "Devdaha Municipality", type: "M", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50802", mofaga: "50802", name: "Butwal Sub-Metropolitan City", type: "SMC", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50803", mofaga: "50803", name: "Sainamaina Municipality", type: "M", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50804", mofaga: "50804", name: "Kanchan Rural Municipality", type: "RM", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50805", mofaga: "50805", name: "Gaidahawa Rural Municipality", type: "RM", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50806", mofaga: "50806", name: "Suddhodhan Rural Municipality", type: "RM", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50807", mofaga: "50807", name: "Siyari Rural Municipality", type: "RM", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50808", mofaga: "50808", name: "Tilottama Municipality", type: "M", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50809", mofaga: "50809", name: "Om Satiya Rural Municipality", type: "RM", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50810", mofaga: "50810", name: "Rohini Rural Municipality", type: "RM", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50811", mofaga: "50811", name: "Siddharthanagar Municipality", type: "M", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50812", mofaga: "50812", name: "Mayadevi Rural Municipality", type: "RM", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50813", mofaga: "50813", name: "Lumbini Sanskritik Municipality", type: "M", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50814", mofaga: "50814", name: "Kotahimai Rural Municipality", type: "RM", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50815", mofaga: "50815", name: "Sammarimai Rural Municipality", type: "RM", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50816", mofaga: "50816", name: "Marchawari Rural Municipality", type: "RM", district: "RUP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50901", mofaga: "50901", name: "Banganga Municipality", type: "M", district: "KAP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50902", mofaga: "50902", name: "Buddhabhumi Municipality", type: "M", district: "KAP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50903", mofaga: "50903", name: "Shivaraj Municipality", type: "M", district: "KAP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50904", mofaga: "50904", name: "Bijayanagar Rural Municipality", type: "RM", district: "KAP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50905", mofaga: "50905", name: "Krishnanagar Municipality", type: "M", district: "KAP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50906", mofaga: "50906", name: "Maharajganj Municipality", type: "M", district: "KAP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50907", mofaga: "50907", name: "Kapilbastu Municipality", type: "M", district: "KAP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50908", mofaga: "50908", name: "Yasodhara Rural Municipality", type: "RM", district: "KAP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50909", mofaga: "50909", name: "Mayadevi Rural Municipality", type: "RM", district: "KAP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF50910", mofaga: "50910", name: "Shuddhodhan Rural Municipality", type: "RM", district: "KAP", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51001", mofaga: "51001", name: "Bangalachuli Rural Municipality", type: "RM", district: "DAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51002", mofaga: "51002", name: "Ghorahi Sub-Metropolitan City", type: "SMC", district: "DAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51003", mofaga: "51003", name: "Tulsipur Sub-Metropolitan City", type: "SMC", district: "DAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51004", mofaga: "51004", name: "Shantinagar Rural Municipality", type: "RM", district: "DAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51005", mofaga: "51005", name: "Babai Rural Municipality", type: "RM", district: "DAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51006", mofaga: "51006", name: "Dangisharan Rural Municipality", type: "RM", district: "DAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51007", mofaga: "51007", name: "Lamahi Municipality", type: "M", district: "DAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51008", mofaga: "51008", name: "Rapti Rural Municipality", type: "RM", district: "DAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51009", mofaga: "51009", name: "Gadhawa Rural Municipality", type: "RM", district: "DAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51010", mofaga: "51010", name: "Rajpur Rural Municipality", type: "RM", district: "DAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51101", mofaga: "51101", name: "Rapti Sonari Rural Municipality", type: "RM", district: "BAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51102", mofaga: "51102", name: "Kohalpur Municipality", type: "M", district: "BAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51103", mofaga: "51103", name: "Baijanath Rural Municipality", type: "RM", district: "BAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51104", mofaga: "51104", name: "Khajura Rural Municipality", type: "RM", district: "BAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51105", mofaga: "51105", name: "Janaki Rural Municipality", type: "RM", district: "BAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51106", mofaga: "51106", name: "Nepalganj Sub-Metropolitan City", type: "SMC", district: "BAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51107", mofaga: "51107", name: "Duduwa Rural Municipality", type: "RM", district: "BAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51108", mofaga: "51108", name: "Narainapur Rural Municipality", type: "RM", district: "BAN", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51201", mofaga: "51201", name: "Bansgadhi Municipality", type: "M", district: "BARD", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51202", mofaga: "51202", name: "Barbardiya Municipality", type: "M", district: "BARD", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51203", mofaga: "51203", name: "Thakurbaba Municipality", type: "M", district: "BARD", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51204", mofaga: "51204", name: "Geruwa Rural Municipality", type: "RM", district: "BARD", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51205", mofaga: "51205", name: "Rajapur Municipality", type: "M", district: "BARD", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51206", mofaga: "51206", name: "Madhuwan Municipality", type: "M", district: "BARD", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51207", mofaga: "51207", name: "Gulariya Municipality", type: "M", district: "BARD", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF51208", mofaga: "51208", name: "Badhaiyatal Rural Municipality", type: "RM", district: "BARD", province: "Lumbini", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60101", mofaga: "60101", name: "Dolpo Buddha Rural Municipality", type: "RM", district: "DOLP", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60102", mofaga: "60102", name: "Shey Phoksundo Rural Municipality", type: "RM", district: "DOLP", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60103", mofaga: "60103", name: "Jagadulla Rural Municipality", type: "RM", district: "DOLP", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60104", mofaga: "60104", name: "Mudkechula Rural Municipality", type: "RM", district: "DOLP", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60105", mofaga: "60105", name: "Tripurasundari Municipality", type: "M", district: "DOLP", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60106", mofaga: "60106", name: "Thulibheri Municipality", type: "M", district: "DOLP", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60107", mofaga: "60107", name: "Kaike Rural Municipality", type: "RM", district: "DOLP", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60108", mofaga: "60108", name: "Chharka Tangsong Rural Municipality", type: "RM", district: "DOLP", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60201", mofaga: "60201", name: "Mugumkarmarog Rural Municipality", type: "RM", district: "MUG", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60202", mofaga: "60202", name: "Chhayanath Rara Municipality", type: "M", district: "MUG", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60203", mofaga: "60203", name: "Soru Rural Municipality", type: "RM", district: "MUG", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60204", mofaga: "60204", name: "Khatyad Rural Municipality", type: "RM", district: "MUG", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60301", mofaga: "60301", name: "Chankheli Rural Municipality", type: "RM", district: "HUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60302", mofaga: "60302", name: "Kharpunath Rural Municipality", type: "RM", district: "HUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60303", mofaga: "60303", name: "Simkot Rural Municipality", type: "RM", district: "HUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60304", mofaga: "60304", name: "Namkha Rural Municipality", type: "RM", district: "HUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60305", mofaga: "60305", name: "Sarkegad Rural Municipality", type: "RM", district: "HUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60306", mofaga: "60306", name: "Adanchuli Rural Municipality", type: "RM", district: "HUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60307", mofaga: "60307", name: "Tanjakot Rural Municipality", type: "RM", district: "HUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60401", mofaga: "60401", name: "Patarasi Rural Municipality", type: "RM", district: "JUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60402", mofaga: "60402", name: "Kanaka Sundari Rural Municipality", type: "RM", district: "JUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60403", mofaga: "60403", name: "Sinja Rural Municipality", type: "RM", district: "JUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60404", mofaga: "60404", name: "Chandannath Municipality", type: "M", district: "JUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60405", mofaga: "60405", name: "Guthichaur Rural Municipality", type: "RM", district: "JUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60406", mofaga: "60406", name: "Tatopani Rural Municipality", type: "RM", district: "JUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60407", mofaga: "60407", name: "Tila Rural Municipality", type: "RM", district: "JUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60408", mofaga: "60408", name: "Hima Rural Municipality", type: "RM", district: "JUM", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60501", mofaga: "60501", name: "Palata Rural Municipality", type: "RM", district: "KAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60502", mofaga: "60502", name: "Pachal Jharana Rural Municipality", type: "RM", district: "KAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60503", mofaga: "60503", name: "Raskot Municipality", type: "M", district: "KAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60504", mofaga: "60504", name: "Sanni Tribeni Rural Municipality", type: "RM", district: "KAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60505", mofaga: "60505", name: "Naraharinath Rural Municipality", type: "RM", district: "KAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60506", mofaga: "60506", name: "Khandachakra Municipality", type: "M", district: "KAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60507", mofaga: "60507", name: "Tilagupha Municipality", type: "M", district: "KAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60508", mofaga: "60508", name: "Mahawai Rural Municipality", type: "RM", district: "KAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60509", mofaga: "60509", name: "Kalika Rural Municipality", type: "RM", district: "KAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60601", mofaga: "60601", name: "Naumule Rural Municipality", type: "RM", district: "DAI", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60602", mofaga: "60602", name: "Mahabu Rural Municipality", type: "RM", district: "DAI", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60603", mofaga: "60603", name: "Bhairabi Rural Municipality", type: "RM", district: "DAI", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60604", mofaga: "60604", name: "Thantikandh Rural Municipality", type: "RM", district: "DAI", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60605", mofaga: "60605", name: "Aathbis Municipality", type: "M", district: "DAI", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60606", mofaga: "60606", name: "Chamunda Bindrasaini Municipality", type: "M", district: "DAI", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60607", mofaga: "60607", name: "Dullu Municipality", type: "M", district: "DAI", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60608", mofaga: "60608", name: "Narayan Municipality", type: "M", district: "DAI", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60609", mofaga: "60609", name: "Bhagawatimai Rural Municipality", type: "RM", district: "DAI", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60610", mofaga: "60610", name: "Dungeshwor Rural Municipality", type: "RM", district: "DAI", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60611", mofaga: "60611", name: "Gurans Rural Municipality", type: "RM", district: "DAI", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60701", mofaga: "60701", name: "Barekot Rural Municipality", type: "RM", district: "JAJ", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60702", mofaga: "60702", name: "Kuse Rural Municipality", type: "RM", district: "JAJ", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60703", mofaga: "60703", name: "Junichande Rural Municipality", type: "RM", district: "JAJ", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60704", mofaga: "60704", name: "Chhedagad Municipality", type: "M", district: "JAJ", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60705", mofaga: "60705", name: "Shivalaya Rural Municipality", type: "RM", district: "JAJ", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60706", mofaga: "60706", name: "Bheri Municipality", type: "M", district: "JAJ", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60707", mofaga: "60707", name: "Nalagad Municipality", type: "M", district: "JAJ", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60801", mofaga: "60801", name: "Aathabisakot Municipality", type: "M", district: "RUKU", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60802", mofaga: "60802", name: "Sanibheri Rural Municipality", type: "RM", district: "RUKU", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60803", mofaga: "60803", name: "Banphikot Rural Municipality", type: "RM", district: "RUKU", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60804", mofaga: "60804", name: "Musikot Municipality", type: "M", district: "RUKU", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60805", mofaga: "60805", name: "Tribeni Rural Municipality", type: "RM", district: "RUKU", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60806", mofaga: "60806", name: "Chaurjahari Municipality", type: "M", district: "RUKU", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60901", mofaga: "60901", name: "Darma Rural Municipality", type: "RM", district: "SAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60902", mofaga: "60902", name: "Kumakh Malika Rural Municipality", type: "RM", district: "SAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60903", mofaga: "60903", name: "Banagad Kupinde Municipality", type: "M", district: "SAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60904", mofaga: "60904", name: "Dhorchaur Rural Municipality", type: "RM", district: "SAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60905", mofaga: "60905", name: "Bagachour Municipality", type: "M", district: "SAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60906", mofaga: "60906", name: "Chhatreshwori Rural Municipality", type: "RM", district: "SAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60907", mofaga: "60907", name: "Sharada Municipality", type: "M", district: "SAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60908", mofaga: "60908", name: "Kalimati Rural Municipality", type: "RM", district: "SAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60909", mofaga: "60909", name: "Tribeni Rural Municipality", type: "RM", district: "SAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF60910", mofaga: "60910", name: "Kapurkot Rural Municipality", type: "RM", district: "SAL", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF61001", mofaga: "61001", name: "Simta Rural Municipality", type: "RM", district: "SUR", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF61002", mofaga: "61002", name: "Chingad Rural Municipality", type: "RM", district: "SUR", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF61003", mofaga: "61003", name: "Lekabeshi Municipality", type: "M", district: "SUR", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF61004", mofaga: "61004", name: "Gurbhakot Municipality", type: "M", district: "SUR", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF61005", mofaga: "61005", name: "Bheriganga Municipality", type: "M", district: "SUR", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF61006", mofaga: "61006", name: "Birendranagar Municipality", type: "M", district: "SUR", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF61007", mofaga: "61007", name: "Barahatal Rural Municipality", type: "RM", district: "SUR", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF61008", mofaga: "61008", name: "Panchapuri Municipality", type: "M", district: "SUR", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF61009", mofaga: "61009", name: "Chaukune Rural Municipality", type: "RM", district: "SUR", province: "Karnali", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70101", mofaga: "70101", name: "Himali Rural Municipality", type: "RM", district: "BAJU", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70102", mofaga: "70102", name: "Gaumul Rural Municipality", type: "RM", district: "BAJU", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70103", mofaga: "70103", name: "Budhinanda Municipality", type: "M", district: "BAJU", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70104", mofaga: "70104", name: "Swami Kartik Rural Municipality", type: "RM", district: "BAJU", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70105", mofaga: "70105", name: "Jagannath Rural Municipality", type: "RM", district: "BAJU", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70106", mofaga: "70106", name: "Badimalika Municipality", type: "M", district: "BAJU", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70107", mofaga: "70107", name: "Khaptad Chhededaha Rural Municipality", type: "RM", district: "BAJU", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70108", mofaga: "70108", name: "Budhiganga Municipality", type: "M", district: "BAJU", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70109", mofaga: "70109", name: "Tribeni Municipality", type: "M", district: "BAJU", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70201", mofaga: "70201", name: "Kanda Rural Municipality", type: "RM", district: "BAJ", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70202", mofaga: "70202", name: "Bungal Municipality", type: "M", district: "BAJ", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70203", mofaga: "70203", name: "Surma Rural Municipality", type: "RM", district: "BAJ", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70204", mofaga: "70204", name: "Talkot Rural Municipality", type: "RM", district: "BAJ", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70205", mofaga: "70205", name: "Masta Rural Municipality", type: "RM", district: "BAJ", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70206", mofaga: "70206", name: "Jayaprithbi Municipality", type: "M", district: "BAJ", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70207", mofaga: "70207", name: "Chhabis Pathibhara Rural Municipality", type: "RM", district: "BAJ", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70208", mofaga: "70208", name: "Durgathali Rural Municipality", type: "RM", district: "BAJ", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70209", mofaga: "70209", name: "Kedarsyun Rural Municipality", type: "RM", district: "BAJ", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70210", mofaga: "70210", name: "Bitthadchir Rural Municipality", type: "RM", district: "BAJ", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70211", mofaga: "70211", name: "Thalara Rural Municipality", type: "RM", district: "BAJ", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70212", mofaga: "70212", name: "Khaptad Chhanna Rural Municipality", type: "RM", district: "BAJ", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70301", mofaga: "70301", name: "Byas Rural Municipality", type: "RM", district: "DAR", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70302", mofaga: "70302", name: "Duhun Rural Municipality", type: "RM", district: "DAR", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70303", mofaga: "70303", name: "Mahakali Municipality", type: "M", district: "DAR", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70304", mofaga: "70304", name: "Naugad Rural Municipality", type: "RM", district: "DAR", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70305", mofaga: "70305", name: "Apihimal Rural Municipality", type: "RM", district: "DAR", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70306", mofaga: "70306", name: "Marma Rural Municipality", type: "RM", district: "DAR", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70307", mofaga: "70307", name: "Shailyashikhar Municipality", type: "M", district: "DAR", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70308", mofaga: "70308", name: "Malikarjun Rural Municipality", type: "RM", district: "DAR", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70309", mofaga: "70309", name: "Lekam Rural Municipality", type: "RM", district: "DAR", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70401", mofaga: "70401", name: "Dilasaini Rural Municipality", type: "RM", district: "BAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70402", mofaga: "70402", name: "Dogada Kedar Rural Municipality", type: "RM", district: "BAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70403", mofaga: "70403", name: "Puchaundi Municipality", type: "M", district: "BAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70404", mofaga: "70404", name: "Surnaya Rural Municipality", type: "RM", district: "BAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70405", mofaga: "70405", name: "Dasharathchand Municipality", type: "M", district: "BAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70406", mofaga: "70406", name: "Pancheshwor Rural Municipality", type: "RM", district: "BAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70407", mofaga: "70407", name: "Shivanath Rural Municipality", type: "RM", district: "BAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70408", mofaga: "70408", name: "Melauli Municipality", type: "M", district: "BAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70409", mofaga: "70409", name: "Patan Municipality", type: "M", district: "BAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70410", mofaga: "70410", name: "Sigas Rural Municipality", type: "RM", district: "BAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70501", mofaga: "70501", name: "Nawadurga Rural Municipality", type: "RM", district: "DAD", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70502", mofaga: "70502", name: "Amargadhi Municipality", type: "M", district: "DAD", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70503", mofaga: "70503", name: "Ajayameru Rural Municipality", type: "RM", district: "DAD", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70504", mofaga: "70504", name: "Bhageshwor Rural Municipality", type: "RM", district: "DAD", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70505", mofaga: "70505", name: "Parashuram Municipality", type: "M", district: "DAD", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70506", mofaga: "70506", name: "Aalital Rural Municipality", type: "RM", district: "DAD", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70507", mofaga: "70507", name: "Ganyapdhura Rural Municipality", type: "RM", district: "DAD", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70601", mofaga: "70601", name: "Purbichouki Rural Municipality", type: "RM", district: "DOT", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70602", mofaga: "70602", name: "Sayal Rural Municipality", type: "RM", district: "DOT", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70603", mofaga: "70603", name: "Aadarsha Rural Municipality", type: "RM", district: "DOT", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70604", mofaga: "70604", name: "Shikhar Municipality", type: "M", district: "DOT", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70605", mofaga: "70605", name: "Dipayal Silgadhi Municipality", type: "M", district: "DOT", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70606", mofaga: "70606", name: "K.I. Singh Rural Municipality", type: "RM", district: "DOT", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70607", mofaga: "70607", name: "Bogatan Rural Municipality", type: "RM", district: "DOT", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70608", mofaga: "70608", name: "Badi Kedar Rural Municipality", type: "RM", district: "DOT", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70609", mofaga: "70609", name: "Jorayal Rural Municipality", type: "RM", district: "DOT", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70701", mofaga: "70701", name: "Panchdebal Binayak Municipality", type: "M", district: "ACH", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70702", mofaga: "70702", name: "Ramaroshan Rural Municipality", type: "RM", district: "ACH", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70703", mofaga: "70703", name: "Mellekh Rural Municipality", type: "RM", district: "ACH", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70704", mofaga: "70704", name: "Sanphebagar Municipality", type: "M", district: "ACH", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70705", mofaga: "70705", name: "Chaurpati Rural Municipality", type: "RM", district: "ACH", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70706", mofaga: "70706", name: "Mangalsen Municipality", type: "M", district: "ACH", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70707", mofaga: "70707", name: "Bannigadhi Jayagadh Rural Municipality", type: "RM", district: "ACH", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70708", mofaga: "70708", name: "Kamal Bazar Municipality", type: "M", district: "ACH", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70709", mofaga: "70709", name: "Dhakari Rural Municipality", type: "RM", district: "ACH", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70710", mofaga: "70710", name: "Turmakhand Rural Municipality", type: "RM", district: "ACH", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70801", mofaga: "70801", name: "Mohanyal Rural Municipality", type: "RM", district: "KAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70802", mofaga: "70802", name: "Chure Rural Municipality", type: "RM", district: "KAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70803", mofaga: "70803", name: "Godawari Municipality", type: "M", district: "KAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70804", mofaga: "70804", name: "Gauriganga Municipality", type: "M", district: "KAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70805", mofaga: "70805", name: "Ghodaghodi Municipality", type: "M", district: "KAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70806", mofaga: "70806", name: "Bardagoriya Rural Municipality", type: "RM", district: "KAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70807", mofaga: "70807", name: "Lamki Chuha Municipality", type: "M", district: "KAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70808", mofaga: "70808", name: "Janaki Rural Municipality", type: "RM", district: "KAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70809", mofaga: "70809", name: "Joshipur Rural Municipality", type: "RM", district: "KAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70810", mofaga: "70810", name: "Tikapur Municipality", type: "M", district: "KAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70811", mofaga: "70811", name: "Bhajani Municipality", type: "M", district: "KAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70812", mofaga: "70812", name: "Kailari Rural Municipality", type: "RM", district: "KAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70813", mofaga: "70813", name: "Dhangadhi Sub-Metropolitan City", type: "SMC", district: "KAI", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70901", mofaga: "70901", name: "Krishnapur Municipality", type: "M", district: "KAN", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70902", mofaga: "70902", name: "Shuklaphanta Municipality", type: "M", district: "KAN", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70903", mofaga: "70903", name: "Bedkot Municipality", type: "M", district: "KAN", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70904", mofaga: "70904", name: "Bhimdatta Municipality", type: "M", district: "KAN", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70905", mofaga: "70905", name: "Mahakali Municipality", type: "M", district: "KAN", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70906", mofaga: "70906", name: "Laljhadi Rural Municipality", type: "RM", district: "KAN", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70907", mofaga: "70907", name: "Punarbas Municipality", type: "M", district: "KAN", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70908", mofaga: "70908", name: "Belouri Municipality", type: "M", district: "KAN", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },
  { pcode: "MF70909", mofaga: "70909", name: "Beldandi Rural Municipality", type: "RM", district: "KAN", province: "Sudur Paschim", src: "MoFAGA local-government list (Luna, 21 Sep 2026)" },

];

/* ---------------------------------------------------------------------
   SITES  -- the data workstream's list of 15 Sep 2026, applied 16 Sep 2026
   source   roster    on the workbook's holding-centre roster sheet (23)
            reported  named in submitted reports, not on that roster (31)
            gov-list  on the DAO Nuwakot list of 29 Bhadra, not on the roster
                      (12). QUESTION D-S14: do these enter the coverage
                      roster? Until ruled they are selectable on the form but
                      NOT in the denominator.
            retired   merged into another code or retired because a palika
                      or a ward is not a site (8). Kept so old records still
                      resolve; never offered on the form.
   palika   the COD-AB pcode, a key into PALIKAS; null = not established
   ward     as sourced; `ward_src` says by whom. A range means the former
            VDC spans several wards and the exact one is not established.
   np       Devanagari as printed in the source named in `np_src`; absent
            where no source carries one -- NOT drafted.
   pop      LEFT NULL IN THIS PUBLIC COPY (unpublished operational figures).
   open     the data workstream's open question on this site, verbatim.
   ------------------------------------------------------------------- */
const SITES = [
  // ---- Rasuwa ----
  { code: "RAS-01", district: "RAS", palika: "NP0329402", ward: "6", ward_src: "[S3 p.211]", name: "District Coordination Committee, Rasuwa (Dhunche)", np: "जिल्ला समन्वय समिति, रसुवा", np_src: "Roster [S1]", pop: null, source: "roster", open: "No report string maps to this site. Still open?" },
  { code: "RAS-02", district: "RAS", palika: "NP0329403", name: "Shantibazar", np: "शान्तिबजार", np_src: "Roster [S1]", pop: null, source: "roster", open: "No report string maps to this site. Not locatable in the administrative sources checked [S3, S6]. Open, and covered by anyone?" },
  { code: "RAS-03", district: "RAS", palika: "NP0329403", ward: "5", ward_src: "[S1] (partner-reported)", name: "Shivalaya (holding centre at Shivalaya Basic School)", np: "शिवालय", np_src: "Roster [S1]", pop: null, source: "roster", open: "Confirm the roster's शिवालय is the holding centre at Shivalaya Basic School, Uttargaya-5." },
  { code: "RAS-04", district: "RAS", palika: "NP0329403", name: "Shree Komin Syambangphel Secondary School", np: "श्री कोमिन श्यामबाङफेल माध्यमिक विद्यालय", np_src: "Roster [S1]", pop: null, source: "roster", open: "Is this the \"Komin, Syafrubesi\" site partners report in Gosaikunda-5 (RAS-R4)? Roster says Uttargaya; Syafrubesi is Gosaikunda-5 [S9]. Until confirmed, reports stay on RAS-R4 and RAS-04 shows no report." },
  // ---- Rasuwa · reported / DAO list ----
  { code: "RAS-R1", district: "RAS", palika: "NP0329403", ward: "5", ward_src: "[S1] (one partner)", name: "Nilkantha Secondary School (holding centre)", pop: null, source: "reported", open: "Devanagari name not in any source obtained." },
  { code: "RAS-R2", district: "RAS", palika: "NP0329403", ward: "5", ward_src: "[S1] (partner-reported)", name: "Bhimsenthan Basic School (holding centre)", pop: null, source: "reported" },
  { code: "RAS-R3", district: "RAS", palika: "NP0329403", ward: "5", ward_src: "[S1]", name: "Shivalaya Basic School, Uttargaya-5", pop: null, source: "retired", merged_into: "RAS-03", open: "See RAS-03." },
  { code: "RAS-R4", district: "RAS", palika: "NP0329402", ward: "5", ward_src: "[S1][S9]", name: "Komin, Syafrubesi", pop: null, source: "reported", open: "Possible identity with roster RAS-04 - confirm." },
  { code: "RAS-R5", district: "RAS", palika: "NP0329404", ward: "3", ward_src: "[S1] (partner-reported)", name: "Sundhara Secondary School", pop: null, source: "reported", open: "Is this the \"Kalika school\" / \"Kalika Holding Centre\" reported by CWIN?" },
  { code: "RAS-R6", district: "RAS", palika: "NP0329404", ward: "3", ward_src: "[S1][S8]", name: "Dharapani (locality), Kalika-3", pop: null, source: "reported", open: "Is there a named holding centre at Dharapani?" },
  { code: "RAS-R7", district: "RAS", palika: "NP0329403", ward: "4", ward_src: "[S1] (partner-reported)", name: "Nava Bijaya Mahendra Secondary School", pop: null, source: "reported" },
  { code: "RAS-R8", district: "RAS", palika: "NP0329403", ward: "4", ward_src: "[S1] (partner-reported)", name: "Dhunge School (reported as \"Dhunge Aa.Bi Secondary School\")", pop: null, source: "reported", open: "Basic or secondary school? The reported name is contradictory." },
  { code: "RAS-R9", district: "RAS", palika: "NP0329403", name: "Barahi Basic School", pop: null, source: "reported" },
  { code: "RAS-R10", district: "RAS", palika: "NP0329403", ward: "4", ward_src: "[S6]", name: "Laharepauwa Health Post (health camp)", pop: null, source: "reported", open: "One partner wrote \"Rasuwa 1 Bogatitar\" (Bogatitar = Uttargaya-5 [S6]). Where was the health camp held?" },
  // ---- Nuwakot ----
  { code: "NUW-01", district: "NUW", palika: "NP0328301", ward: "9", ward_src: "[S2][S1] (DAO camp location) ; roster lists 8 and 9", name: "Bhairam (Bhairum) Secondary School", np: "भैरम मा.वि., बिदुर-०८, बिदुर-०९", np_src: "Roster [S1]", pop: null, source: "roster", open: "DAO lists this school together with the Colony covered hall (NUW-08) as one camp. Has NUW-08 merged into NUW-01?" },
  { code: "NUW-02", district: "NUW", palika: "NP0328301", ward: "9", ward_src: "[S1] (roster)", name: "Church, Bidur Colony-9", np: "चर्च , बिदुर कोलोनी -०९", np_src: "Roster [S1]", pop: null, source: "roster", open: "Not on the DAO list of 29 Bhadra [S2] and no report maps to it. Closed or uncovered?" },
  { code: "NUW-03", district: "NUW", palika: "NP0328301", ward: "9", ward_src: "[S1] (roster)", name: "Sparkle Academy", np: "स्पार्कल एकेडेमी, बिदुर-०९", np_src: "Roster [S1]", pop: null, source: "roster", open: "Not on the DAO list. Same school as DAO's \"Star Boarding, Colony\" (NUW-27), which CMC-Nepal calls Star Academy?" },
  { code: "NUW-04", district: "NUW", palika: "NP0328301", ward: "9", ward_src: "[S1][S2]", name: "Trishuli Basic School", np: "त्रिशुली आ.वि., बिदुर ०९", np_src: "Roster [S1]", pop: null, source: "roster" },
  { code: "NUW-05", district: "NUW", palika: "NP0328301", ward: "9", ward_src: "[S2]", name: "Sulakshana Secondary School", np: "सुलक्षणा मा.वि. (roster); शुलक्षणा मा.वि. (DAO)", np_src: "Roster [S1]; DAO [S2]", pop: null, source: "roster" },
  { code: "NUW-06", district: "NUW", palika: "NP0328301", ward: "2", ward_src: "[S1][S2]", name: "Pitrimoksha - Kriyaputri Bhawan / Safe House (near District Administration Office)", np: "पितृमोक्ष (जिल्ला प्रशासन कार्यालय नजिक), बिदुर-२", np_src: "Roster [S1]", pop: null, source: "roster", open: "TPO Nepal writes \"Pitri Mokshya Kriyaputri Bhawan\" (one place). DAO lists \"सेफहाउस/क्रियापुत्रि भवन\" as one camp at Bidur-2. But KOSHISH (Bhadra 13 meeting note) lists \"Kriyaputribhawan\" and \"Safe house\" in Bidur-2 as two of seven centres. Confirm: is the Safe House a separate centre?" },
  { code: "NUW-07", district: "NUW", palika: "NP0328301", ward: "5", ward_src: "[S2]", name: "Chandrajyoti Secondary School", np: "चन्द्रज्योति मा.वि., बिदुर नगरपालिका", np_src: "Roster [S1]", pop: null, source: "roster" },
  { code: "NUW-08", district: "NUW", palika: "NP0328301", ward: "9", ward_src: "[S1][S2] (inferred)", name: "Covered Hall, Colony-9", np: "कभर्ड हल, कोलोनी ९", np_src: "Roster [S1]", pop: null, source: "roster", open: "DAO lists \"Colony covered hall / Bhairum school\" as one camp (see NUW-01)." },
  { code: "NUW-09", district: "NUW", palika: "NP0328301", ward: "2", ward_src: "[S2][S1] (DAO camp location) ; roster names the Bidur-4 Battar area", name: "Covered Hall (hosting Battar, Bidur-4)", np: "कभर्ड हल बिदुर ४ बट्टार क्षेत्र, बिदुर नगरपालिका", np_src: "Roster [S1]", pop: null, source: "roster", open: "Partners call it \"Battar kabaddi hall\", \"Taekwondo hall, Bidur-2\" and \"Taekwondo covered hall, Battar\". Confirm these are one building." },
  { code: "NUW-10", district: "NUW", palika: "NP0328301", ward: "5", ward_src: "[S1][S2][S6]", name: "Ayurveda and Alternative Hospital, Devighat", np: "आयुर्वेद तथा वैकल्पिक चिकित्सालय, देविघाट, बिदुर-५", np_src: "Roster [S1]", pop: null, source: "roster" },
  { code: "NUW-11", district: "NUW", palika: "NP0328301", ward: "10", ward_src: "[S2]", name: "Sundari Kyaureni Secondary School (Gerkhutar)", np: "सुन्दरी ब्योरिनी मा.वि. (roster); सुन्दरि क्यौरीनि मा.वि. (DAO)", np_src: "Roster [S1]; DAO [S2]", pop: null, source: "roster", open: "Confirm the roster spelling ब्योरिनी is a typing error." },
  { code: "NUW-12", district: "NUW", palika: "NP0328301", name: "Ranabhuneshwari Secondary School / Ward Office", np: "रणभुनेश्र्वरी मा.वि./वडा कार्यालय, बिदुर नगरपालिका", np_src: "Roster [S1]", pop: null, source: "roster", open: "Not on the DAO list and no report maps to it. Closed or uncovered?" },
  { code: "NUW-13", district: "NUW", palika: "NP0328402", ward: "5", ward_src: "[S1][S2]", name: "Tribhuvan Secondary School (Archale)", np: "त्रिभुवन मा.वि., किस्पाङ ०५", np_src: "Roster [S1]", pop: null, source: "roster" },
  { code: "NUW-14", district: "NUW", palika: "NP0328402", ward: "5", ward_src: "[S1] (roster)", name: "Karki Manakamana Basic School", np: "कार्की मनकामना आ.वि. ०५, किस्पाङ गाउँपालिका", np_src: "Roster [S1]", pop: null, source: "roster", open: "Not on the DAO list; no report names it (two Kispang-5 records name no site)." },
  { code: "NUW-15", district: "NUW", palika: "NP0328302", ward: "7", ward_src: "[S3]", name: "Mahadev Secondary School, Ratmate", np: "महादेव मा.वि. रातमाटे, बेलकोटगढी न.पा.", np_src: "Roster [S1]", pop: null, source: "roster", open: "DAO lists \"Mahadev Campus, Mahadev Phant\" (NUW-29) and \"Shiladevi Secondary School, Ratmate\" (NUW-30) in ward 7 but no Mahadev Secondary School. CWIN names \"Mahadev School\" and \"Mahadev Campus\" as two holding centres (row 54) - so NUW-15 and NUW-29 are kept apart. Is the school still open?" },
  { code: "NUW-16", district: "NUW", palika: "NP0328301", ward_src: "[S3] 7, 8 or 9 (not established)", name: "Janakalyan Samuha, Tupche", np: "जनकल्याण समुह तुप्चे", np_src: "Roster [S1]", pop: null, source: "roster" },
  { code: "NUW-17", district: "NUW", palika: "NP0328301", ward: "4", ward_src: "[S2]", name: "Tamang Plaza, Battar", np: "तामाङ प्लाजा ४ (roster); तामाङ प्लाजा विदुर ४ बट्टार (DAO)", np_src: "Roster [S1]; DAO [S2]", pop: null, source: "roster" },
  { code: "NUW-18", district: "NUW", palika: "NP0328301", ward: "7", ward_src: "[S3] (inferred)", name: "Community Building, Akhare, Tupche", np: "सामुदायिक भवन अखरे तुप्चे ७", np_src: "Roster [S1]", pop: null, source: "roster", open: "Is this the camp DAO lists as \"Library/Health Post, Tupchetar\" (NUW-26)?" },
  { code: "NUW-19", district: "NUW", palika: "NP0328301", ward: "7", ward_src: "[S3] (inferred)", name: "Church, Dandathoktar, Tupche", np: "चर्च डाँडाथोकटार, तुप्चे ७", np_src: "Roster [S1]", pop: null, source: "roster" },
  { code: "NUW-20", district: "NUW", palika: "NP0328301", ward: "1", ward_src: "[S2]", name: "Indrayani Basic School", np: "इन्दायणी आ.वि. विदुर १", np_src: "DAO [S2]", pop: null, source: "gov-list" },
  { code: "NUW-21", district: "NUW", palika: "NP0328301", ward: "2", ward_src: "[S2]", name: "Health Post, Bidur-2 (Nuwakot Darbar)", np: "स्वास्थ्य चौकी विदुर २ नुवाकोट दरबार", np_src: "DAO [S2]", pop: null, source: "gov-list" },
  { code: "NUW-22", district: "NUW", palika: "NP0328301", ward: "3", ward_src: "[S2]", name: "Chandi Basic School, Mairitar", np: "चण्डी आ.वी मैरिटार", np_src: "DAO [S2]", pop: null, source: "gov-list", open: "No report names it." },
  { code: "NUW-23", district: "NUW", palika: "NP0328301", ward: "2", ward_src: "[S2]", name: "Annapurna Panchakanya Basic School", np: "अन्नपुर्ण पञ्चकन्या आ.वि", np_src: "DAO [S2]", pop: null, source: "gov-list", open: "No report names it." },
  { code: "NUW-24", district: "NUW", palika: "NP0328301", ward: "4", ward_src: "[S2]", name: "United Basic School", np: "युनाइटेड आधारभुत विद्यालय", np_src: "DAO [S2]", pop: null, source: "gov-list" },
  { code: "NUW-25", district: "NUW", palika: "NP0328301", ward: "6", ward_src: "[S2]", name: "Battar Chautara / Chisyan Kendra (cold store)", np: "बट्टार चौतारा/ चिस्यान केन्द्र", np_src: "DAO [S2]", pop: null, source: "gov-list", open: "No report names it." },
  { code: "NUW-26", district: "NUW", palika: "NP0328301", ward: "7", ward_src: "[S2]", name: "Library / Health Post, Tupchetar", np: "लाईबेरी/स्वास्थ्य चौकी तुप्चेटार", np_src: "DAO [S2]", pop: null, source: "gov-list", open: "Relation to roster Tupche sites NUW-16, NUW-18, NUW-19?" },
  { code: "NUW-27", district: "NUW", palika: "NP0328301", ward: "9", ward_src: "[S2]", name: "Star Boarding School, Colony", np: "स्टार बोर्डिङ कोलोनि", np_src: "DAO [S2]", pop: null, source: "gov-list", open: "Same school as roster NUW-03 Sparkle Academy? CMC-Nepal writes \"Star Academy\"." },
  { code: "NUW-28", district: "NUW", palika: "NP0328301", ward: "10", ward_src: "[S2]", name: "Khamare Syale, Keraghari", np: "खमारे स्याले, केराघारी", np_src: "DAO [S2]", pop: null, source: "gov-list", open: "No report names it." },
  { code: "NUW-29", district: "NUW", palika: "NP0328302", ward: "7", ward_src: "[S2]", name: "Mahadev Campus, Mahadev Phant", np: "महादेव क्याम्पस महादेव फाँट", np_src: "DAO [S2]", pop: null, source: "gov-list", open: "See NUW-15." },
  { code: "NUW-30", district: "NUW", palika: "NP0328302", ward: "7", ward_src: "[S2]", name: "Shiladevi Secondary School, Ratmate", np: "शिलादेवी मा वि रातमाटे", np_src: "DAO [S2]", pop: null, source: "gov-list", open: "No report names it. See NUW-15." },
  { code: "NUW-31", district: "NUW", palika: "NP0328302", ward: "8", ward_src: "[S2]", name: "Janasewa Basic School", np: "जनसेवा आ. वि", np_src: "DAO [S2]", pop: null, source: "gov-list", open: "TPO Nepal calls it \"Paachkhaal Holding Center\"; CWIN calls it \"Janasewa campus\"." },
  // ---- Nuwakot · reported / DAO list ----
  { code: "NUW-R1", district: "NUW", palika: "NP0328301", ward: "2", name: "Kriyaputri Bhawan / Safe Home", pop: null, source: "retired", merged_into: "NUW-06", open: "See NUW-06. KOSHISH also names a \"Bidur 2-UHC\" among Bidur-2 centres - not established what it is." },
  { code: "NUW-R2", district: "NUW", palika: "NP0328301", name: "Samudayik Bahuudeshya Bhawan (community multipurpose building) holding centre", pop: null, source: "reported", open: "Not on the DAO list by this name. Which DAO camp is it?" },
  { code: "NUW-R3", district: "NUW", palika: "NP0328301", ward: "9", ward_src: "[S1] (partner-reported)", name: "Trishuli Hospital (including its OCMC)", pop: null, source: "reported", open: "A health facility service point, not a holding centre." },
  { code: "NUW-R4", district: "NUW", palika: "NP0328301", ward: "4", name: "Battar Kabaddi Hall", pop: null, source: "retired", merged_into: "NUW-09", open: "See NUW-09." },
  { code: "NUW-R5", district: "NUW", palika: "NP0328302", ward: "7", name: "Belkotgadhi Municipality-7", pop: null, source: "retired", retired_reason: "palika-level coding" },
  { code: "NUW-R6", district: "NUW", palika: "NP0328301", ward: "2", ward_src: "[S1] (partner-reported)", name: "Rani Mauri Hotel", pop: null, source: "reported" },
  { code: "NUW-R7", district: "NUW", palika: "NP0328302", ward: "7", ward_src: "[S3]", name: "Ratmate Church", pop: null, source: "reported" },
  { code: "NUW-R8", district: "NUW", palika: null, name: "Himalayan School", pop: null, source: "reported", open: "Palika not stated." },
  { code: "NUW-R9", district: "NUW", palika: null, name: "Siyale holding centre", pop: null, source: "reported", open: "Palika not stated." },
  { code: "NUW-R10", district: "NUW", palika: "NP0328301", name: "Patanjali Yog Bhawan", pop: null, source: "reported" },
  // ---- Dhading · reported / DAO list ----
  { code: "DHA-R1", district: "DHA", palika: "NP0330410", ward: "4", ward_src: "[S1] (partner-reported)", name: "Dhading Multiple Campus holding centre, Mastar", pop: null, source: "reported" },
  { code: "DHA-R2", district: "DHA", palika: "NP0330410", name: "Galchhi RM (community-based)", pop: null, source: "retired", retired_reason: "palika-level coding" },
  { code: "DHA-R3", district: "DHA", palika: "NP0330409", name: "Gajuri RM", pop: null, source: "retired", retired_reason: "palika-level coding" },
  { code: "DHA-R4", district: "DHA", palika: "NP0330408", name: "Benighat Rorang RM", pop: null, source: "retired", retired_reason: "palika-level coding" },
  { code: "DHA-R5", district: "DHA", palika: "NP0330409", ward: "5", ward_src: "[S1] (partner-reported)", name: "Galaudi holding centre (Sub-division Forest Office premises)", pop: null, source: "reported", open: "Is \"Galdhu holding centre, Gajuri RM\" (CMC-Nepal) the same place?" },
  { code: "DHA-R6", district: "DHA", palika: "NP0330409", ward: "5", ward_src: "[S1] (partner-reported)", name: "Ratomate (Ratamata) holding centre, Phokrakhola", pop: null, source: "reported" },
  { code: "DHA-R7", district: "DHA", palika: "NP0330410", ward: "4-7", ward_src: "[S3] (not established)", name: "Success Academy, Baireni", pop: null, source: "reported" },
  { code: "DHA-R8", district: "DHA", palika: "NP0330410", ward: "6", ward_src: "[S1] (partner-reported)", name: "Bageshwori Secondary School, Baireni", pop: null, source: "reported" },
  { code: "DHA-R9", district: "DHA", palika: "NP0330408", ward: "5", ward_src: "[S1] (partner-reported)", name: "Chandrodaya Secondary School", pop: null, source: "reported" },
  { code: "DHA-R10", district: "DHA", palika: "NP0330410", ward: "6", ward_src: "[S6]", name: "Baireni Hospital", pop: null, source: "reported" },
  { code: "DHA-R11", district: "DHA", palika: "NP0330407", ward: "6", ward_src: "[S1] (partner-reported)", name: "Satyawati Secondary School", pop: null, source: "reported", open: "Named only in a two-site record." },
  { code: "DHA-R12", district: "DHA", palika: "NP0330407", ward: "6", ward_src: "[S1] (partner-reported)", name: "Mahakali Secondary School", pop: null, source: "reported", open: "Named only in a two-site record." },
  // ---- Kathmandu · reported / DAO list ----
  { code: "KTM-R1", district: "KTM", palika: "NP0327101", ward: "15", ward_src: "[S1] (partner-reported)", name: "Mustang Gumba holding centre, Swayambhu", pop: null, source: "reported" },
  { code: "KTM-R2", district: "KTM", palika: null, name: "Yellow Gumba", pop: null, source: "reported" },
  { code: "KTM-R3", district: "KTM", palika: null, name: "Geeta Mata School (children from Yellow Gumba and Mustang Gumba)", pop: null, source: "reported" },
  { code: "KTM-R4", district: "KTM", palika: null, name: "Nepal Buddhist Dharma Service Association premises", pop: null, source: "reported", open: "Confirm it is a service point." },
  // ---- Chitwan · reported / DAO list ----
  { code: "CHT-R1", district: "CHT", palika: "NP0335101", name: "Bharatpur", pop: null, source: "retired", retired_reason: "palika-level coding" },
  // ---- Nawalparasi (Bardaghat Susta East) · reported / DAO list ----
  { code: "NAW-R1", district: "NAW", palika: null, name: "Madhyabindu Provincial Hospital", pop: null, source: "reported" },
  // ---- Sindhupalchok · reported / DAO list ----
  { code: "SIN-R1", district: "SIN", palika: "NP0323302", ward: "4-7", ward_src: "[S3] (not established)", name: "Chautara Hospital", pop: null, source: "reported", open: "Outside the flood-affected districts in the workbook. Does this KOSHISH record belong to the flood response?" },

  { code: "OTHER", district: "OTH", name: "Other — not on this list (specify below)", pop: null, source: "escape", np: "अन्य", np_src: "draft" },
];

/* ---------------------------------------------------------------------
   ACTIVITIES — the list agreed on 17 September 2026 (activity list v3)
   ---------------------------------------------------------------------
   ONE ACTIVITY, TWO READINGS. The field form shows `name` and `help` in
   plain language and nothing else. The register, the dashboard's backend
   view and every export read the SAME code through the IASC fields:
     layer / group   the IASC intervention pyramid layer (IASC Guidelines
                     2007, pp. 11-13) -- ACTIVITY_GROUPS below
     iasc_sub        the IASC 4Ws 2012 Table 2 subcode, when the match is
                     direct; it travels on the record as `iascSub`
     iasc_of         the candidate subcodes when the subcode is set at
                     coordination from the description -- the reporter is
                     never asked; the record carries no subcode until then
     iasc_rule       how the subcode is set
   The reporter never sees an IASC term; the coordinator never sees only a
   plain label. Both readings point at one code, so they cannot drift.

   Code = layer.item, stored as TEXT ("3.1", never a number). First digit =
   layer 1-4; x.9 = Other (describe) within the layer, so no code shifts
   when an item is added; "9" = fits no layer. These are NOT 4Ws codes:
   3.1 here is PFA, 4Ws subcode 3.1 is community-initiated social support.
   The 4Ws subcode labels are IASC_4WS_SUBCODES, as printed in Table 2.

   Three copies of one list, changed together: this file; the master JSON
   MHPSS_Nepal_ActivityCategories_IASC_17Sep2026.json and its .xlsx in
   Information Management/; the project note claude/activity-categories.md
   (choosing rules R1-R15, the crosswalk, sources S1-S4). The subject
   expert of the Ministry (EDCD) leads the categorisation and may still
   change labels or placement. Nepali labels wait for the health-sector
   glossary requested at the EDCD review of 17 Sep 2026.
   ------------------------------------------------------------------- */
const ACTIVITY_GROUPS = [
  { code: "1", name: "Information and basic services", np: "सूचना र आधारभूत सेवा", np_src: "draft",        iasc_layer: "i",   iasc_name: "Basic services and security",          me2017: "Social considerations in basic services and security" },
  { code: "2", name: "Community and family activities", np: "समुदाय र परिवारका गतिविधि", np_src: "draft",       iasc_layer: "ii",  iasc_name: "Community and family supports",        me2017: "Strengthening community and family supports" },
  { code: "3", name: "Support for individuals and families", np: "व्यक्ति र परिवारका लागि सहयोग", np_src: "draft",  iasc_layer: "iii", iasc_name: "Focused, non-specialised supports",    me2017: "Focused (person-to-person) non-specialised supports" },
  { code: "4", name: "Specialist mental health care", np: "विशेषज्ञ मानसिक स्वास्थ्य सेवा", np_src: "draft",         iasc_layer: "iv",  iasc_name: "Specialised services",                 me2017: "Specialised services" },
  { code: "9", name: "Other activity", np: "अन्य गतिविधि", np_src: "draft",                        iasc_layer: null,  iasc_name: null,                                   me2017: null },
];
const ACTIVITIES = [
  { code: "1.1", group: "1", name: "Information on where to get help",       help: "Helpline numbers, services, relief updates", help_np: "हेल्पलाइन नम्बर, सेवा, राहत अद्यावधिक", np: "सहयोग कहाँ पाइन्छ भन्ने जानकारी", np_src: "draft",
    iasc_sub: "1.1", iasc_rule: "Direct." },
  { code: "1.2", group: "1", name: "Orientation for other relief teams",     help: "Shelter, WASH, health or protection staff: safe and respectful treatment of affected people (not training of your own team)", help_np: "आश्रय, WASH, स्वास्थ्य वा संरक्षण कर्मचारी: प्रभावित व्यक्तिसँग सुरक्षित र सम्मानजनक व्यवहार (आफ्नै टोलीको तालिम होइन)", np: "अन्य राहत टोलीलाई अभिमुखीकरण", np_src: "draft",
    iasc_sub: "6.1", iasc_rule: "Direct." },
  { code: "1.9", group: "1", name: "Other (describe)", other: true,           help: "", help_np: "", np: "अन्य (विवरण दिनुहोस्)", np_src: "draft",
    iasc_of: ["1.3", "2.1", "2.2", "2.3", "6.2"], iasc_rule: "Set at coordination from the description: 2.1 support for emergency relief initiated by the community; 2.2 support for communal spaces or meetings; otherwise 1.3, 2.3 or 6.2 (Other)." },
  { code: "2.1", group: "2", name: "Recreational activities",                 help: "Play, art, sports, games; child-friendly space", help_np: "खेल, कला, खेलकुद; बालमैत्री स्थल", np: "मनोरञ्जनात्मक गतिविधि", np_src: "draft",
    iasc_of: ["3.5", "4.1"], iasc_rule: "4.1 when the activity takes place at a child-friendly space; 3.5 otherwise (4Ws 3.5 excludes activities at child-friendly spaces)." },
  { code: "2.2", group: "2", name: "Psychoeducation or awareness (group)",    help: "Stress, coping, self-care; IEC materials on these topics", help_np: "तनाव, सामना गर्ने उपाय, आत्म-हेरचाह; यी विषयका IEC सामग्री", np: "मनोशिक्षा वा जनचेतना (समूह)", np_src: "draft",
    iasc_sub: "1.2", iasc_rule: "Direct. Psychoeducation for one person or family is 3.3." },
  { code: "2.3", group: "2", name: "Community and family support",            help: "Support groups, parenting sessions, women and girls safe space, traditional or religious support", help_np: "सहयोग समूह, अभिभावकत्व सत्र, महिला तथा किशोरी सुरक्षित स्थल, परम्परागत वा धार्मिक सहयोग", np: "समुदाय र परिवार सहयोग", np_src: "draft",
    iasc_of: ["3.1", "3.2", "3.3", "3.4", "3.6", "3.7", "4.2"], iasc_rule: "Set at coordination from the description: 3.1 community-initiated social support; 3.2 parenting or family supports; 3.3 community supports to vulnerable people; 3.4 structured social activities; 3.6 early childhood development; 3.7 traditional, spiritual or religious supports; 4.2 (Other) safe spaces, such as women and girls safe spaces." },
  { code: "2.9", group: "2", name: "Other (describe)", other: true,           help: "", help_np: "", np: "अन्य (विवरण दिनुहोस्)", np_src: "draft",
    iasc_of: ["3.8", "5.1", "5.2", "5.3"], iasc_rule: "Set at coordination from the description: 5.1 psychosocial support to teachers or other school personnel; 5.2 to classes or groups of children at school; otherwise 3.8 or 5.3 (Other)." },
  { code: "3.1", group: "3", name: "Psychological first aid (PFA)",          help: "", help_np: "",
    iasc_sub: "7.1", iasc_rule: "Direct. Same term as the IASC.", np: "मनोवैज्ञानिक प्राथमिक उपचार", np_src: "draft", np_note: "PFA has an official WHO Nepali translation -- adopt ITS term, do not keep ours" },
  { code: "3.2", group: "3", name: "Psychosocial counselling",                help: "Individual, family or group", help_np: "व्यक्तिगत, पारिवारिक वा सामूहिक", np: "मनोसामाजिक परामर्श", np_src: "draft",
    iasc_of: ["8.1", "8.2"], iasc_rule: "8.1 individual; 8.2 group or family. Can be set only if the form records which." },
  { code: "3.3", group: "3", name: "Emotional support",                       help: "Listening, relaxation, home visits, psychoeducation for one person or family", help_np: "सुन्ने, विश्राम अभ्यास, घर भेट, एक व्यक्ति वा परिवारका लागि मनोशिक्षा", np: "भावनात्मक सहयोग", np_src: "draft",
    iasc_of: ["7.3", "8.6"], iasc_rule: "No subcode of its own: 7.3 (Other, person-focused psychosocial work) or 8.6 (Other, psychological intervention), set at coordination with the description." },
  { code: "3.4", group: "3", name: "Screening and referral",                  help: "Finding people who need more help, linking them to services, follow-up", help_np: "थप सहयोग चाहिने व्यक्ति पहिचान, सेवासँग जोड्ने, अनुगमन", np: "स्क्रिनिङ र प्रेषण (रेफर)", np_src: "draft",
    iasc_of: ["7.2", "9.3"], iasc_rule: "7.2 linking vulnerable individuals or families to resources, with follow-up; 9.3 community workers identifying and referring people with mental disorders." },
  { code: "3.5", group: "3", name: "Basic mental health care by general health staff", help: "Assessment or medicines by a trained doctor or nurse who is not a mental health specialist", help_np: "मानसिक स्वास्थ्य विशेषज्ञ नभएका तालिमप्राप्त चिकित्सक वा नर्सद्वारा मूल्याङ्कन वा औषधि", np: "सामान्य स्वास्थ्यकर्मीद्वारा आधारभूत मानसिक स्वास्थ्य सेवा", np_src: "draft",
    iasc_of: ["9.1", "9.2"], iasc_rule: "9.2 when medicines are given; 9.1 otherwise. Can be set only if the form records whether medicines were given." },
  { code: "3.9", group: "3", name: "Other (describe)", other: true,           help: "", help_np: "", np: "अन्य (विवरण दिनुहोस्)", np_src: "draft",
    iasc_of: ["7.3", "8.3", "8.5", "8.6", "9.4"], iasc_rule: "Set at coordination from the description: 8.3 interventions for alcohol or substance use problems; 8.5 psychological debriefing (not offered: the IASC Guidelines 2007, p. 15, advise against one-off, single-session debriefing for the general population); otherwise 7.3, 8.6 or 9.4 (Other)." },
  { code: "4.1", group: "4", name: "Psychotherapy",                           help: "By a clinical psychologist or other mental health professional", help_np: "क्लिनिकल साइकोलोजिस्ट वा अन्य मानसिक स्वास्थ्य पेसाकर्मीद्वारा", np: "मनोचिकित्सा (साइकोथेरापी)", np_src: "draft",
    iasc_sub: "8.4", iasc_rule: "Direct. Same term as the IASC. 4Ws Annex 3: psychological intervention is level 4 only if it involves formal psychotherapy; basic counselling is 3.2." },
  { code: "4.2", group: "4", name: "Psychiatric medication",                  help: "Prescribed or reviewed by a psychiatrist", help_np: "मनोचिकित्सक (साइकियाट्रिस्ट) द्वारा सिफारिस वा समीक्षा गरिएको", np: "मनोरोग औषधि", np_src: "draft",
    iasc_sub: "10.2", iasc_rule: "Direct. Medicines from trained general health staff are 3.5." },
  { code: "4.3", group: "4", name: "Specialist consultation or hospital care", help: "Psychiatrist or clinical psychologist consultation, psychiatric nursing, hospital admission", help_np: "मनोचिकित्सक वा क्लिनिकल साइकोलोजिस्टको परामर्श, मनोरोग नर्सिङ, अस्पताल भर्ना", np: "विशेषज्ञ परामर्श वा अस्पताल सेवा", np_src: "draft",
    iasc_of: ["10.1", "10.3"], iasc_rule: "10.3 inpatient mental health care; 10.1 otherwise." },
  { code: "4.9", group: "4", name: "Other (describe)", other: true,           help: "", help_np: "", np: "अन्य (विवरण दिनुहोस्)", np_src: "draft",
    iasc_sub: "10.4", iasc_rule: "Direct (Other)." },
  { code: "9",   group: "9", name: "Other activity (describe)", other: true,  help: "", help_np: "", np: "अन्य गतिविधि (विवरण दिनुहोस्)", np_src: "draft",
    iasc_of: [], iasc_rule: "No IASC equivalent until the description is reviewed at coordination." },
];

/* The 4Ws 2012 Table 2 subcode labels as printed (transcribed by the data
   workstream from the PDF text layer and checked against the page image);
   only the subcodes an option above can carry. Codes 11.x are not on the
   field form (coordination, assessment, training, supervision, staff care,
   research carry no count of affected people). */
const IASC_4WS_SUBCODES = {
  "1.1": "Information on the current situation, relief efforts or available services in general",
  "1.2": "Raising awareness on mental health and psychosocial support (e.g., messages on positive coping or on available mental health services and psychosocial supports)",
  "1.3": "Other",
  "2.1": "Support for emergency relief that is initiated by the community",
  "2.2": "Support for communal spaces/meetings to discuss, problem-solve and plan action by community members to respond to the emergency",
  "2.3": "Other",
  "3.1": "Support for social support activities that are initiated by the community",
  "3.2": "Strengthening parenting/family supports",
  "3.3": "Facilitation of community supports to vulnerable people",
  "3.4": "Structured social activities (e.g. group activities)",
  "3.5": "Structured recreational or creative activities (do not include activities at child-friendly spaces that are covered in 4.1)",
  "3.6": "Early childhood development (ECD) activities",
  "3.7": "Facilitation of conditions for indigenous traditional, spiritual or religious supports, including communal healing practices",
  "3.8": "Other",
  "4.1": "Child-friendly spaces",
  "4.2": "Other",
  "5.1": "Psychosocial support to teachers / other personnel at schools/learning places",
  "5.2": "Psychosocial support to classes/groups of children at schools/learning places",
  "5.3": "Other",
  "6.1": "Orientation of or advocacy with aid workers/agencies on including social/ psychosocial considerations in programming",
  "6.2": "Other",
  "7.1": "Psychological first aid (PFA)",
  "7.2": "Linking vulnerable individuals/families to resources (e.g., health services, livelihoods assistance, community resources etc.) and following up to see if support is provided.",
  "7.3": "Other",
  "8.1": "Basic counselling for individuals",
  "8.2": "Basic counselling for groups or families",
  "8.3": "Interventions for alcohol/substance use problems",
  "8.4": "Psychotherapy",
  "8.5": "Individual or group psychological debriefing",
  "8.6": "Other",
  "9.1": "Non-pharmacological management of mental disorder by nonspecialized health care providers",
  "9.2": "Pharmacological management of mental disorder by nonspecialized health care providers",
  "9.3": "Action by community workers to identify and refer people with mental disorders and to follow-up on them to make sure adherence to clinical treatment",
  "9.4": "Other",
  "10.1": "Non-pharmacological management of mental disorder by specialized mental health care providers",
  "10.2": "Pharmacological management of mental disorder by specialized health care",
  "10.3": "Inpatient mental health care",
  "10.4": "Other",
};

/* The previous list (codes.js 0.1.0 to 0.3.0 and the reconciliation
   worksheet), kept so that every record already in the register still
   resolves to a name. `to` is the crosswalk of claude/activity-categories.md
   section 7: ONE target and the dashboard reads the record under the new
   code; several targets and the record stays "not yet placed" until someone
   reads its description -- nothing is picked by default; none and the code
   is not an activity of the field form at all. */
const ACTIVITIES_V03 = [
  { code: "PFA",   retired: true, to: ["3.1"],                     name: "Psychological first aid",               np: "मनोवैज्ञानिक प्राथमिक उपचार", np_src: "draft" },
  { code: "CNS-I", retired: true, to: ["3.2"],                     name: "Individual psychosocial counselling",   np: "व्यक्तिगत मनोसामाजिक परामर्श", np_src: "draft" },
  { code: "CNS-G", retired: true, to: ["3.2"],                     name: "Group psychosocial counselling",        np: "सामूहिक मनोसामाजिक परामर्श", np_src: "draft" },
  { code: "PSED",  retired: true, to: ["2.2", "3.3"],              name: "Psychoeducation / awareness session",   np: "मनोशिक्षा / जनचेतना सत्र", np_src: "draft" },
  { code: "RECR",  retired: true, to: ["2.1"],                     name: "Recreational / structured activity",    np: "मनोरञ्जनात्मक / संरचित क्रियाकलाप", np_src: "draft" },
  { code: "CFS",   retired: true, to: ["2.1"],                     name: "Child-friendly space activity",         np: "बालमैत्री क्षेत्रको क्रियाकलाप", np_src: "draft" },
  { code: "SPEC",  retired: true, to: ["4.3", "4.1", "3.5"],       name: "Specialised mental health service",     np: "विशेषज्ञ मानसिक स्वास्थ्य सेवा", np_src: "draft" },
  { code: "MEDS",  retired: true, to: ["4.2", "3.5"],              name: "Psychotropic medication provision",     np: "मनोरोग औषधि उपलब्ध गराइएको", np_src: "draft" },
  { code: "REF",   retired: true, to: ["3.4"],                     name: "Referral made to another service",      np: "अन्य सेवामा प्रेषण (रेफर)", np_src: "draft" },
  { code: "HELP",  retired: true, to: [],                          name: "Helpline contact",                      np: "हेल्पलाइन सम्पर्क", np_src: "draft", note: "a setting, not an activity (R13)" },
  { code: "IEC",   retired: true, to: ["1.1", "2.2"],              name: "IEC material distribution",             np: "सूचना-शिक्षा-सञ्चार सामग्री वितरण", np_src: "draft" },
  { code: "ASMT",  retired: true, to: ["3.4"],                     name: "Rapid assessment / identification",     np: "द्रुत आकलन / पहिचान", np_src: "draft", note: "3.4 when it counts people screened; a situation assessment is not on the field form (R5)" },
  { code: "COORD", retired: true, to: [],                          name: "Coordination meeting",                  np: "समन्वय बैठक", np_src: "draft", note: "not on the field form (R1)" },
  { code: "TRAIN", retired: true, to: [],                          name: "Training / orientation delivered",      np: "तालिम / अभिमुखीकरण सञ्चालन", np_src: "draft", note: "not on the field form (R14), unless orientation of other sectors' staff (1.2)" },
  { code: "STAFF", retired: true, to: [],                          name: "Support to responders / staff care",    np: "कार्यकर्तालाई सहयोग / स्टाफ केयर", np_src: "draft", note: "not on the field form (4Ws 11.5)" },
  { code: "OTH",   retired: true, to: ["1.9", "2.9", "3.9", "4.9", "9"], name: "Other — specify",                np: "अन्य — उल्लेख गर्नुहोस्", np_src: "draft" },
  { code: "CNS",       retired: true, to: ["3.2"], name: "Counselling, individual or group not stated" },
  { code: "PSS-OTHER", retired: true, to: ["3.3"], name: "Other psychosocial support (emotional support, home visits, relaxation)" },
  { code: "SUPERV",    retired: true, to: [],      name: "Supervision", note: "not on the field form (4Ws 11.4)" },
  { code: "GENERIC",   retired: true, to: [],      name: "Generic label only", note: "not codable (R6)" },
  { code: "NONE",      retired: true, to: [],      name: "No activity written", note: "not codable" },
];

/* ---------------------------------------------------------------------
   ORGANISATIONS — providers appearing in submitted reports
   `name`     as partners write it: what the dropdown shows and what a
              report is matched on.
   `official` the registered name where the data workstream verified it on
              the organisation's own site [S14]; absent = not established.
   `donors`   the funding tags seen alongside the provider name. The same
              organisation reporting under two donor tags is a funding
              attribution, NOT two organisations — the de-duplication check
              relies on this distinction. One record carries two tags at
              once (D-O05).
   `partners` organisations written as joint-activity partners, not donors
              (IASC Table 1 item C) -- recorded here until the record schema
              carries a partners field (D-O04).
   OPEN: D-O02 (GOVPSC). KMC, one record, is entered under OTHER with the
   name "KMC" until it is identified (D-O06). Ruling R-O1 on SaMi is open.
   ------------------------------------------------------------------- */
const ORGS = [
  { code: "TPO",    name: "TPO Nepal",                              official: "Transcultural Psychosocial Organization Nepal (TPO Nepal)", type: "National NGO", donors: ["UNICEF", "Save the Children"], partners: ["Madhyabindu Provincial Hospital (facility partner)"] },
  { code: "CMC",    name: "CMC-Nepal",                              official: "Centre for Mental Health and Counseling-Nepal (CMC-Nepal)", type: "National NGO", donors: ["SDC", "UNICEF", "UNFPA", "AWO"], note: "AWO = AWO International e.V.; its funding link to CMC-Nepal is as reported by CMC-Nepal and not visible on either public website." },
  { code: "CWIN",   name: "CWIN Nepal",                             official: "Child Workers in Nepal Concerned Centre (CWIN-Nepal)", type: "National NGO", donors: ["UNICEF"], partners: ["National Federation of Psychosocial Counsellors Nepal (as written; not found in public sources)"] },
  { code: "NRCS",   name: "Nepal Red Cross Society",                type: "National society", donors: [], note: "Expansion not re-verified in this pass. Reports mostly at district or palika level." },
  { code: "KOS",    name: "KOSHISH",                                type: "National NGO", donors: [], note: "Official full name not established (secondary sources only)." },
  { code: "SAMI",   name: "SaMi – Safer Migration Programme",       official: "Safer Migration (SaMi) Programme, bilateral Government of Nepal–Switzerland programme; local governments implementing it appoint and mobilise psychosocial counsellors [S13]", type: "Government programme (palika-appointed counsellors)", donors: [], ruling: "R-O1 open: record the implementing agency as SaMi, or as the rural municipality that appoints the counsellor? The two strings naming Galchhi RM counsellors are probably this programme; confirm with Galchhi RM." },
  { code: "VID",    name: "Vidushi Psychological Support Center",   type: "Not established", donors: [], note: "Spelt as the partner writes it; no official page found." },
  { code: "GOVPSC", name: "Government-deployed counsellor (EDCD)",  type: "Not established", donors: [], question: "D-O02", note: "No record in the report sheet supports this label; the strings behind the inventory's Palika PSC name Galchhi RM counsellors. Retire unless a report shows EDCD-deployed counsellors." },
  { code: "OTHER",  name: "Other — not on this list (specify)",     donors: [], np: "अन्य", np_src: "draft" },
];

/* Funding tags seen in reports. "Save the Children" sat in the remarks
   column of five TPO Nepal records and was missing here (D-O01). */
/* Funding tags. Removed from the FIELD form on 17 Sep 2026 (EDCD): funding
   is collected from the organisations, not from workers on the ground. The
   list stays for the records already held and for the reconciliation
   lists; no form offers it. */
const DONORS = ["UNICEF", "SDC", "UNFPA", "AWO", "Save the Children", "Own funds", "Other", "Not specified"];

/* Cadre of the person delivering — absent from the current form, which is
   why counsellor, psychologist and psychiatrist cannot be counted apart. */
const CADRES = [
  /* The cadre list approved by the Coordinator on 17 Sep 2026 (afternoon):
     EDCD's list of the morning review, plus the cadres Nepal's own system
     names and EDCD's list left out (psychiatric nurse, CPSW, FCHV, the
     mhGAP-trained prescriber). The IASC 4Ws form has no cadre item -- this
     field is our addition -- so each code carries the two frames the world
     counts in: `layer` = the IASC pyramid layer that delivers it
     (specialised / focused / community; the 4Ws activity codes 9 and 10
     draw the same specialist / non-specialist line) and `atlas` = the WHO
     Mental Health Atlas workforce category, so the dashboard can roll up
     either way without touching the codes. Two points are still with EDCD
     and are NOT decided here: whether PSY stays a code of its own, and
     whether VOL splits into PFA volunteers and other trained volunteers. */
  { code: "PSYT", name: "Psychiatrist", np: "मनोचिकित्सक", np_src: "draft", layer: "specialised", iasc_code: "10", atlas: "psychiatrist" },
  { code: "CPSY", name: "Clinical psychologist", np: "क्लिनिकल मनोविद्", np_src: "draft", np_note: "क्लिनिकल साइकोलोजिस्ट is also in use -- one has to be chosen", layer: "specialised", iasc_code: "10", atlas: "psychologist", src: "EDCD review 17 Sep 2026" },
  { code: "PSY",  name: "Psychologist (non-clinical)", np: "मनोविद्", np_src: "draft", np_note: "मनोवैज्ञानिक is also current -- one has to be chosen and used consistently", layer: "specialised", iasc_code: "10", atlas: "psychologist", question: "EDCD 17 Sep: confirm it stays a separate code" },
  { code: "PNUR", name: "Psychiatric / mental health nurse", np: "मानसिक स्वास्थ्य नर्स", np_src: "draft", layer: "specialised", iasc_code: "10", atlas: "mental health nurse", src: "Nepal cadre (district hospital deployments); data workstream ruling R-W1; approved 17 Sep 2026" },
  { code: "MO",   name: "Medical officer / doctor, mhGAP-trained (prescriber)", np: "मेडिकल अफिसर / चिकित्सक (mhGAP तालिमप्राप्त)", np_src: "draft", layer: "focused", iasc_code: "9", atlas: "other medical doctor", src: "Nepal mhGAP prescriber cadre; approved 17 Sep 2026 as an optional split of HW" },
  { code: "HW",   name: "Health worker, non-specialist (nurse, ANM, AHW, HA)", np: "स्वास्थ्यकर्मी, विशेषज्ञ नभएको (नर्स, अनमी, अहेब, हे.अ.)", np_src: "draft", layer: "focused", iasc_code: "9", atlas: "nurse / other health worker" },
  { code: "PSC",  name: "Psychosocial counsellor (NHTC-certified)", np: "मनोसामाजिक परामर्शकर्ता", np_src: "draft", np_note: "cadre title -- check against the NHTC psychosocial counsellor training curriculum", layer: "focused", iasc_code: null, atlas: "other paid mental health worker" },
  { code: "CPSW", name: "Community psychosocial worker", np: "सामुदायिक मनोसामाजिक कार्यकर्ता", np_src: "draft", layer: "focused", iasc_code: null, atlas: "other paid mental health worker", src: "Nepal cadre; data workstream ruling R-W1; approved 17 Sep 2026" },
  { code: "SW",   name: "Social worker", np: "सामाजिक कार्यकर्ता", np_src: "draft", layer: "focused", iasc_code: null, atlas: "social worker" },
  { code: "FCHV", name: "Female community health volunteer", np: "महिला सामुदायिक स्वास्थ्य स्वयंसेविका", np_src: "draft", layer: "community", iasc_code: null, atlas: null, src: "Nepal government cadre; approved 17 Sep 2026" },
  { code: "VOL",  name: "Trained volunteer (including PFA volunteers)", np: "तालिम प्राप्त स्वयंसेवक (PFA स्वयंसेवकसहित)", np_src: "draft", layer: "community", iasc_code: null, atlas: null, question: "EDCD 17 Sep: confirm whether PFA volunteers and other trained volunteers are two codes" },
  { code: "OTH",  name: "Other — specify", np: "अन्य — उल्लेख गर्नुहोस्", np_src: "draft", layer: null, iasc_code: null, atlas: null },
  /* retired 17 Sep 2026 (merged into PSC): kept so records that carry it still resolve; never offered on a form */
  { code: "SPSC", name: "Senior psychosocial counsellor", np: "वरिष्ठ मनोसामाजिक परामर्शकर्ता", np_src: "draft", retired: true, mergeInto: "PSC", layer: "focused", iasc_code: null, atlas: "other paid mental health worker" },
];

/* Target groups — category codes only. Never a description of a person. */
const TARGET_GROUPS = [
  { code: "TG-BER", name: "Families of missing or deceased persons", np: "बेपत्ता वा मृतकका परिवार", np_src: "draft" },
  { code: "TG-DIS", name: "Displaced households at a holding centre or shelter", np: "आश्रयस्थल वा अस्थायी शिविरमा रहेका विस्थापित परिवार", np_src: "draft" },
  { code: "TG-COM", name: "Affected community, general", np: "प्रभावित समुदाय, सामान्य", np_src: "draft" },
  { code: "TG-CHI", name: "Children and adolescents", np: "बालबालिका र किशोरकिशोरी", np_src: "draft" },
  { code: "TG-OLD", name: "Older people", np: "ज्येष्ठ नागरिक", np_src: "draft", np_note: "the statutory term in Nepal -- confirm it is what MoH wants on a form" },
  { code: "TG-PWD", name: "People with disabilities", np: "अपाङ्गता भएका व्यक्ति", np_src: "draft", np_note: "check against the Act Relating to Rights of Persons with Disabilities 2017 wording" },
  { code: "TG-PEX", name: "People with a pre-existing mental health condition", np: "पहिलेदेखि मानसिक स्वास्थ्य समस्या भएका व्यक्ति", np_src: "draft" },
  { code: "TG-RES", name: "Frontline responders (SAR, army, police, volunteers, forensic, health)", np: "अग्रपङ्क्तिका कार्यकर्ता (खोज-उद्धार, सेना, प्रहरी, स्वयंसेवक, फोरेन्सिक, स्वास्थ्य)", np_src: "draft" },
  { code: "TG-PRG", name: "Pregnant and postpartum women", np: "गर्भवती र सुत्केरी महिला", np_src: "draft" },
  { code: "TG-OTH", name: "Other group — specify", np: "अन्य समूह — उल्लेख गर्नुहोस्", np_src: "draft", src: "EDCD review 17 Sep 2026: Other on every list" },
];

/* Service setting — where the activity took place. The four settings agreed
   with EDCD on 17 Sep 2026, chosen so a field worker can tell them apart
   and so the form outlives the emergency: holding centres are temporary,
   facilities are not. Telephone / helpline stays, because the helpline
   reports on the same form. The earlier codes are retired, not deleted, so
   a record that carries one still reads. */
const MODALITIES = [
  { code: "HC",  name: "In person — holding centre", np: "प्रत्यक्ष — होल्डिङ सेन्टर", np_src: "draft", src: "EDCD review 17 Sep 2026" },
  { code: "COM", name: "In person — outreach in the community", np: "प्रत्यक्ष — समुदायमा पहुँच सेवा", np_src: "draft", src: "EDCD review 17 Sep 2026" },
  { code: "FAC", name: "In person — facility (health facility, school, hospital, OCMC, other government facility)", np: "प्रत्यक्ष — संस्थामा (स्वास्थ्य संस्था, विद्यालय, अस्पताल, OCMC, अन्य सरकारी निकाय)", np_src: "draft", src: "EDCD review 17 Sep 2026" },
  { code: "TEL", name: "Telephone / helpline", np: "टेलिफोन / हेल्पलाइन", np_src: "draft" },
  { code: "OTH", name: "Other — specify", np: "अन्य — उल्लेख गर्नुहोस्", np_src: "draft" },
  { code: "INP", name: "In person, at a site (code retired 17 Sep 2026)", np: "प्रत्यक्ष, सेवा स्थलमा", np_src: "draft", retired: true },
  { code: "OUT", name: "In person, outreach / mobile (code retired 17 Sep 2026)", np: "प्रत्यक्ष, घुम्ती / पहुँच सेवा", np_src: "draft", retired: true },
];

const STATUS = [
  { code: "ONG", name: "Ongoing", np: "चालु", np_src: "draft" },
  { code: "CMP", name: "Completed", np: "सम्पन्न", np_src: "draft" },
  { code: "PLN", name: "Planned", np: "योजनामा", np_src: "draft" },
];

/* One cadre per person. Some people on the four workforce lists carry
   different labels in different lists, and the lists are undated, so
   "most recent wins" cannot be applied; the workstream's ruling R-W1 is
   that the most specialised label wins, in this order (D-C03).
   OPEN: D-C01 psychiatric nurse and D-C02 community psychosocial worker
   have no code and are entered as OTH until ruled. */
const CADRE_RANK = ["PSYT", "CPSY", "PSY", "PNUR", "MO", "HW", "PSC", "CPSW", "SW", "FCHV", "VOL", "OTH"];

/* Convenience lookups */
const siteByCode = Object.fromEntries(SITES.map((s) => [s.code, s]));
const orgByCode = Object.fromEntries(ORGS.map((o) => [o.code, o]));
const districtByCode = Object.fromEntries(DISTRICTS.map((d) => [d.code, d]));
const activityByCode = Object.fromEntries(ACTIVITIES.concat(ACTIVITIES_V03).map((a) => [a.code, a]));
const activityGroupByCode = Object.fromEntries(ACTIVITY_GROUPS.map((g) => [g.code, g]));

/* THE TWO READINGS OF ONE ACTIVITY CODE.
   activityResolve(code) answers, for any code old or new, where a record
   is read on the dashboard: `placed` is the current code it counts under
   (itself for a current code; the single crosswalk target for a retired
   code with one; null when it is not yet placed or not an activity).
   activityIasc(code) is the backend reading: the IASC layer and the 4Ws
   subcode(s), as words, for a current code. */
function activityResolve(code) {
  var a = activityByCode[code];
  if (!a) return { code: code || "", name: code || "", legacy: false, placed: null, to: [], note: "unknown code" };
  if (!a.retired) return { code: a.code, name: a.name, legacy: false, placed: a.code, to: [a.code], group: a.group };
  var to = a.to || [];
  var placed = to.length === 1 ? to[0] : null;
  return { code: a.code, name: a.name, legacy: true, placed: placed, to: to,
           group: placed ? activityByCode[placed].group : null,
           note: to.length === 0 ? (a.note || "not an activity of the field form") : to.length === 1 ? "read as " + placed : "not yet placed: " + to.join(" or ") };
}
function activityIasc(code) {
  var a = activityByCode[code];
  if (!a || a.retired) return "";
  var g = activityGroupByCode[a.group];
  var layer = g && g.iasc_layer ? "Layer " + g.iasc_layer + " — " + g.iasc_name : "No IASC layer";
  var sub = a.iasc_sub ? "4Ws " + a.iasc_sub + " " + (IASC_4WS_SUBCODES[a.iasc_sub] || "")
          : (a.iasc_of && a.iasc_of.length) ? "4Ws " + a.iasc_of.join(" / ") + " — set at coordination"
          : "no 4Ws subcode until the description is reviewed";
  return layer + " · " + sub;
}
const palikaByCode = Object.fromEntries(PALIKAS.map((p) => [p.pcode, p]));

/* Roster sites only — the denominator for coverage-gap analysis.
   A site that is merely "reported" cannot be counted as uncovered,
   because nobody ever said it should be covered. Whether the DAO-listed
   centres ("gov-list") join this denominator is open (D-S14); until it is
   ruled they are offered on the forms and kept out of the denominator. */
const ROSTER_SITES = SITES.filter((s) => s.source === "roster");

/* What a form may offer: everything except a retired code. A retired code
   stays in SITES so that an old record still resolves to a name; it is
   never a choice for a new one. */
const FORM_SITES = SITES.filter((s) => s.source !== "retired");

/* ---------------------------------------------------------------------
   Exposed as a global rather than an ES module on purpose: the form has
   to open straight from a file on a laptop, with no server, and browsers
   refuse ES module imports over file://. Offline-from-a-USB-stick is a
   requirement here, not a convenience.
   ------------------------------------------------------------------- */
/* ---------------------------------------------------------------------
   THE LABEL RESOLVER — one place that decides which language a code list
   shows in.
   ---------------------------------------------------------------------
   Every dropdown in every form was built from `it.name`, which is always
   English. So the Nepali site names already in this file -- 23 of them,
   written by someone who knows the places -- never appeared anywhere: the
   Nepali page still showed the English name. Adding `np` to the other
   lists would have been dead weight for the same reason.

   Now a list item carries `np` and this function picks it when the page
   is in Nepali, so adding a Nepali label to any list makes it appear in
   every form at once. Same principle as the string dictionary: one copy,
   one place, and no page has to remember.

   `np_src` records where the Nepali came from:
     "confirmed"  checked against a Nepali-language source, named in the
                  comment above the list
     "draft"      our rendering, NOT yet confirmed against an official
                  Nepali term -- the page says so, and these are what the
                  worksheet asks a Nepali speaker to check first
   Absent `np` falls back to English rather than showing a blank, because
   a field worker facing an empty dropdown cannot report at all.
   ------------------------------------------------------------------- */
function isNepali() {
  try { return document.documentElement.getAttribute("data-lang") === "ne"; }
  catch (e) { return false; }
}
function label(it) {
  if (it == null) return "";
  if (typeof it === "string") return it;
  if (isNepali() && it.np) return it.np;
  return it.name || "";
}
/* A dropdown's first line -- "Select…", "All districts". See the
   placeholders note in assets/i18n-strings.js for why these are matched by
   their English text and why that is temporary. Anything unmatched is
   returned unchanged and warned about once, so it stays visible. */
var phMissed = {};
function ph(txt) {
  if (!txt || !isNepali()) return txt;
  var map = (window.I18N_STRINGS && window.I18N_STRINGS._meta &&
             window.I18N_STRINGS._meta.placeholders) || {};
  if (map[txt]) return map[txt];
  if (!phMissed[txt]) {
    phMissed[txt] = 1;
    try { console.warn("[codes] placeholder with no Nepali:", txt); } catch (e) {}
  }
  return txt;
}

/* the lookup form: a code, and the list it belongs to */
function labelOf(list, code) {
  if (!list || !code) return code || "";
  for (var i = 0; i < list.length; i++) {
    if (list[i] && list[i].code === code) return label(list[i]);
  }
  return code;
}
/* How much of each list exists in Nepali, and how much of that is still a
   draft. Reported by tools/i18n-check.py so the code lists are counted
   next to the prose rather than being invisible to it. */
function npCoverage() {
  var out = {};
  [["SITES", SITES], ["PALIKAS", PALIKAS], ["DISTRICTS", DISTRICTS], ["ACTIVITIES", ACTIVITIES],
   ["CADRES", CADRES], ["TARGET_GROUPS", TARGET_GROUPS],
   ["MODALITIES", MODALITIES], ["STATUS", STATUS], ["ORGS", ORGS]
  ].forEach(function (pair) {
    var list = pair[1], np = 0, draft = 0;
    list.forEach(function (it) {
      if (it && it.np) { np++; if (it.np_src !== "confirmed") draft++; }
    });
    out[pair[0]] = { total: list.length, np: np, draft: draft };
  });
  return out;
}

/* A site's palika as words. `site.palika` is a P-code so that maps and the
   NDRRMA 5W join on it; nobody should have to read one. */
function palikaName(pcode) {
  var p = palikaByCode[pcode];
  return p ? label(p) : "";
}

window.CODES = {
  META, DISTRICTS, PALIKAS, SITES, ACTIVITIES, ACTIVITY_GROUPS, ACTIVITIES_V03, IASC_4WS_SUBCODES, ORGS, DONORS, CADRES, CADRE_RANK,
  TARGET_GROUPS, MODALITIES, STATUS,
  siteByCode, orgByCode, districtByCode, activityByCode, activityGroupByCode, palikaByCode,
  ROSTER_SITES, FORM_SITES,
  activityResolve, activityIasc,
  label, labelOf, palikaName, ph, npCoverage
};
