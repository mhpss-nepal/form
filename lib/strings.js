/* ---------------------------------------------------------------------
   form/lib/strings.js

   The strings this form needs that hub/assets/i18n-strings.js does not yet
   carry, plus the few whose wording changed with the activity grid.

   Why it exists: the new fields went onto the form while the hub repository
   was left alone, so ten labels rendered on the live page as [f4.newLab],
   [f4.roleLab] and the like, in both languages. This file is loaded straight
   after the hub strings and fills or replaces those keys.

   It is a debt, not a design, like lib/store.js beside it. When hub carries
   these strings, delete this file and the script tag in 5ws-report.html.

   FILL  = added only when hub has nothing, so hub wins the moment it does.
   SET   = replaced on purpose, because the wording on this form changed and
           hub still carries the older sentence.

   The Nepali is a machine draft awaiting a translator, as agreed on
   21 September 2026.
   --------------------------------------------------------------------- */
(function () {
  "use strict";
  var T = window.I18N_STRINGS;
  if (!T || !T.en || !T.ne) return;

  var FILL = {
    en: {
      "f4.tgHelp": "Ticking \"Persons with disabilities\" opens the disability question just below, and that is the only place the disability counts are entered.",
      "f4.ofPwdHelp": "Help needed at the time, not disability status. The disability counts are at the top, under the target groups.",
      "f4.tgHelp": "\u0905\u092a\u093e\u0919\u094d\u0917\u0924\u093e \u092d\u090f\u0915\u093e \u0935\u094d\u092f\u0915\u094d\u0924\u093f \u091a\u093f\u0939\u094d\u0928 \u0932\u0917\u093e\u090f\u092a\u091b\u093f \u0924\u0932 \u0905\u092a\u093e\u0919\u094d\u0917\u0924\u093e\u0938\u092e\u094d\u092c\u0928\u094d\u0927\u0940 \u092a\u094d\u0930\u0936\u094d\u0928 \u0916\u0941\u0932\u094d\u091b, \u0930 \u0905\u0919\u094d\u0915 \u0924\u094d\u092f\u0939\u0940\u0902 \u092e\u093e\u0924\u094d\u0930 \u092d\u0930\u094d\u0928\u0947 \u0939\u094b\u0964",
      "f4.ofPwdHelp": "\u0924\u094d\u092f\u0938 \u0938\u092e\u092f \u0938\u0939\u092f\u094b\u0917 \u091a\u093e\u0939\u093f\u090f\u0915\u094b, \u0905\u092a\u093e\u0919\u094d\u0917\u0924\u093e\u0915\u094b \u0905\u0935\u0938\u094d\u0925\u093e \u0939\u094b\u0908\u0928\u0964 \u0905\u092a\u093e\u0919\u094d\u0917\u0924\u093e\u0915\u094b \u0905\u0919\u094d\u0915 \u092e\u093e\u0925\u093f \u091b\u0964",
      "f4.disWho": "Of the people here today",
      "f4.disRowName": "With a disability",
      "f4.disRowHelp": "Count what you can see, or what the person tells you. The type of disability is not asked.",
      "f4.disCaption": "Persons with disabilities here today, by sex and by age",
      "f4.disWho": "\u0906\u091c \u092f\u0939\u093e\u0901 \u092d\u090f\u0915\u093e\u092e\u0927\u094d\u092f\u0947",
      "f4.disRowName": "\u0905\u092a\u093e\u0919\u094d\u0917\u0924\u093e \u092d\u090f\u0915\u093e",
      "f4.disRowHelp": "\u091c\u0947 \u0926\u0947\u0916\u094d\u0928\u0941\u0939\u0941\u0928\u094d\u091b, \u0935\u093e \u0935\u094d\u092f\u0915\u094d\u0924\u093f\u0906\u092b\u0948\u0932\u0947 \u092d\u0928\u0947\u0915\u094b \u0906\u0927\u093e\u0930\u092e\u093e \u0917\u0928\u094d\u0928\u0941\u0939\u094b\u0938\u094d\u0964 \u0905\u092a\u093e\u0919\u094d\u0917\u0924\u093e\u0915\u094b \u0915\u093f\u0938\u093f\u092e \u0938\u094b\u0927\u093f\u0928\u094d\u0928\u0964",
      "f4.disCaption": "\u0906\u091c \u092f\u0939\u093e\u0901 \u092d\u090f\u0915\u093e \u0905\u092a\u093e\u0919\u094d\u0917\u0924\u093e \u092d\u090f\u0915\u093e \u0935\u094d\u092f\u0915\u094d\u0924\u093f, \u0932\u093f\u0919\u094d\u0917 \u0930 \u0909\u092e\u0947\u0930\u0905\u0928\u0941\u0938\u093e\u0930",
      "f4.newLab": "Of whom new today",
      "f4.newHelp": "People here today taking part for the first time. Required every day. It sits inside the day's figure and is never added to it.",
      "f4.roleLab": "Who reports the figures",
      "f4.roleLead": "We led this activity — we report the figures",
      "f4.rolePartner": "We took part — the lead organisation reports the figures",
      "f4.roleHelp": "On a joint activity only the lead fills the counts, so one session is never counted twice. A partner report carries no figures; name the lead above.",
      "f4.roleHeld": "The lead organisation reports the figures for this activity, so the counts are switched off here.",
      "f4.ageHelp": "Five age groups: 0–4, 5–9, 10–17, 18–59, 60+. Leave a row blank rather than partly filled; within a row the sex total and the age total are checked against each other.",
      "f4.rollUnder18": "under 18",
      "f4.rollOver18": "18 and over",
      "f4.hActivity": "Activity",
      "f4.hSexGrp": "Sex",
      "f4.hAgeGrp": "Age",
      "f4.allAct": "All activities",
      "f4.gridHelp": "Fill a row for each activity that ran at this site today. Within a row, sex and age are two counts of the same people, so the two totals must agree. Leave a row blank if that activity did not run.",
      "f4.gridCaption": "Activities, with the people who took part counted by sex and by age",
      "f4.describeThis": "Describe this activity",
      "f4.describePh": "What was done, in a few words — no names",
      "f4.h3hint": "one row per activity that ran today",
      "sr.age.10to17": "10–17",
      "sr.age.18to59": "18–59"
    },
    ne: {
      "f4.newLab": "यसमध्ये आज नयाँ",
      "f4.newHelp": "आज यहाँ पहिलो पटक सहभागी भएका व्यक्ति। हरेक दिन अनिवार्य। यो दिनको संख्याभित्रै पर्छ, थपिँदैन।",
      "f4.roleLab": "अङ्क कसले प्रतिवेदन गर्छ",
      "f4.roleLead": "हामीले नेतृत्व गरेको — अङ्क हामी प्रतिवेदन गर्छौँ",
      "f4.rolePartner": "हामी सहभागी मात्र — अङ्क नेतृत्व गर्ने संस्थाले प्रतिवेदन गर्छ",
      "f4.roleHelp": "संयुक्त गतिविधिमा नेतृत्व गर्ने संस्थाले मात्र अङ्क भर्छ, त्यसैले एउटै सत्र दोहोरो गनिँदैन। सहभागीको प्रतिवेदनमा अङ्क हुँदैन।",
      "f4.roleHeld": "नेतृत्व गर्ने संस्थाले यस गतिविधिको अङ्क प्रतिवेदन गर्छ, त्यसैले यहाँ अङ्क भर्ने खाली बन्द गरिएको छ।",
      "f4.ageHelp": "पाँच उमेर समूह: ०–४, ५–९, १०–१७, १८–५९, ६०+। पङ्क्ति आधा भर्नुभन्दा खाली छोड्नुहोस्।",
      "f4.rollUnder18": "१८ वर्षमुनि",
      "f4.rollOver18": "१८ वर्ष र माथि",
      "f4.hActivity": "गतिविधि",
      "f4.hSexGrp": "लिङ्ग",
      "f4.hAgeGrp": "उमेर",
      "f4.allAct": "सबै गतिविधि",
      "f4.gridHelp": "आज यस स्थानमा चलेका हरेक गतिविधिको एउटा पङ्क्ति भर्नुहोस्। एउटै पङ्क्तिभित्र लिङ्ग र उमेर एउटै व्यक्तिहरूको दुई गणना हुन्, त्यसैले दुवैको जम्मा मिल्नुपर्छ।",
      "f4.gridCaption": "गतिविधि, सहभागी व्यक्ति लिङ्ग र उमेरअनुसार",
      "f4.describeThis": "यो गतिविधि वर्णन गर्नुहोस्",
      "f4.describePh": "के गरियो, छोटोमा — नाम नलेख्नुहोस्",
      "f4.h3hint": "आज चलेका हरेक गतिविधिको एउटा पङ्क्ति",
      "sr.age.10to17": "१०–१७",
      "sr.age.18to59": "१८–५९"
    }
  };

  /* Wording that changed with the grid: one report is now one day at one
     site, so "Attendance" became "People here today, counted once", and the
     tally reads the largest activity row rather than a disaggregated sum. */
  var SET = {
    en: {
      "f4.ofPwd": "Needed help to move or get around",
      "f4.ofPwd": "\u0939\u093f\u0901\u0921\u0921\u0941\u0932 \u0935\u093e \u092f\u0924\u093e\u0909\u0924\u093e \u091c\u093e\u0928 \u0938\u0939\u092f\u094b\u0917 \u091a\u093e\u0939\u093f\u090f\u0915\u094b",
      "f4.disNote": "Sex and age are two counts of the same people here too, so the two totals are checked against each other. They sit inside the day\u2019s figure and are never added to it or to the activity rows.",
      "f4.disNote": "\u092f\u0939\u093e\u0901 \u092a\u0928\u093f \u0932\u093f\u0919\u094d\u0917 \u0930 \u0909\u092e\u0947\u0930 \u090f\u0909\u091f\u0948 \u0935\u094d\u092f\u0915\u094d\u0924\u093f\u0939\u0930\u0942\u0915\u094b \u0926\u0941\u0908 \u0917\u0923\u0928\u093e \u0939\u0941\u0928\u094d, \u0924\u094d\u092f\u0938\u0948\u0932\u0947 \u0926\u0941\u0935\u0948\u0915\u094b \u091c\u092e\u094d\u092e\u093e \u092e\u093f\u0932\u094d\u0928\u0941\u092a\u0930\u094d\u091b\u0964 \u092f\u0940 \u0926\u093f\u0928\u0915\u094b \u0938\u0902\u0916\u094d\u092f\u093e\u092d\u093f\u0924\u094d\u0930\u0948 \u092a\u0930\u094d\u091b\u0928\u094d, \u0925\u092a\u093f\u0901\u0926\u0948\u0928\u0928\u094d\u0964",
      "f4.reachLab": "People here today, counted once",
      "f4.reachHelp": "Everyone who took part at this site today, each person counted once however many activities they joined. It is never smaller than the largest activity row, and never larger than all the rows added together.",
      "f4.tally": "Largest activity row",
      "f4.disSession": "Were the people here today asked about disability?",
      "f4.h3what": "What was done"
    },
    ne: {
      "f4.reachLab": "आज यहाँ भएका व्यक्ति, एक पटक मात्र गनिएको",
      "f4.reachHelp": "आज यस स्थानमा सहभागी भएका सबै, जतिसुकै गतिविधिमा सहभागी भए पनि एक पटक मात्र गनिने।",
      "f4.tally": "सबैभन्दा ठूलो गतिविधि पङ्क्ति",
      "f4.disSession": "आज यहाँ भएका व्यक्तिहरूलाई अपाङ्गताबारे सोधिएको थियो?",
      "f4.h3what": "के गरियो"
    }
  };

  ["en", "ne"].forEach(function (lang) {
    Object.keys(FILL[lang]).forEach(function (k) {
      if (T[lang][k] === undefined || T[lang][k] === null || T[lang][k] === "") T[lang][k] = FILL[lang][k];
    });
    Object.keys(SET[lang]).forEach(function (k) { T[lang][k] = SET[lang][k]; });
  });
})();
