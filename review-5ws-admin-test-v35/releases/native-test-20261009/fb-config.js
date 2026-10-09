/* =====================================================================
   Firebase configuration — MHPSS Nepal
   ---------------------------------------------------------------------
   Project: mhpss-nepal-hub. Written from the Firebase console on
   15 September 2026.

   This file is public, and that is expected: a Firebase web config is
   not a secret. It identifies the project; it does not grant access.
   Access is decided entirely by the Firestore security rules, which
   live in Information Management/firestore_rules_mhpss_nepal_v1.txt
   and are published from the console. Those rules are tested — 40 cases
   covering identity keys, timestamps, location precision and read
   access — before anything is deployed.

   NEVER put a service-account key or any private key in this file.
   ===================================================================== */
window.FB_CONFIG = {
  apiKey: "AIzaSyBa0Z1SPwkP-vwA6-icqmC1gIfI0aLOaI8",
  authDomain: "mhpss-nepal-hub.firebaseapp.com",
  projectId: "mhpss-nepal-hub",
  storageBucket: "mhpss-nepal-hub.firebasestorage.app",
  messagingSenderId: "39288227570",
  appId: "1:39288227570:web:4259bf73ceedbda16e326b"
};

/* One collection, one document per record, keyed by a deterministic id
   so a retried write overwrites itself instead of duplicating. */
window.FB_COLLECTION = "submissions";
