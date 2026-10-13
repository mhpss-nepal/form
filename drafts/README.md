# Drafts — not live, not linked

Four field forms built in September 2026, parked here so they are not lost and not lost track of.
None is linked from any index, and the register scripts have been removed from all four, so nothing
typed into them can reach the retired register.

| File | What it is | What it still needs |
|---|---|---|
| `contact.html` | Service contact record, with the referral block folded in (decision of 23 September) | Person-level. Under the decision of 11 October it runs only in a per-organisation locked house, and only once the written basis from EDCD and the TWG exists. Built for the Firestore era |
| `referral-outcome.html` | The short follow-up: did the person arrive, and if not, what got in the way | Same conditions as above |
| `service-point.html` | Registration of a place where an organisation works, for the referral directory | Service-level. Needs adapting to the preview-isolation, trial-scope and QR conventions now on main |
| `provider-register.html` | Self-registration of a named provider, on consent | Service-level, but the consent wording is a draft to be settled by the Coordinator with EDCD |

The Nepali in all four is a machine draft awaiting a translator.

## How these four relate to the files at the repository root

`contact.html` and `referral.html` at the root are the 21 September versions, and they are
still the ones the indexes point to. `drafts/contact.html` is the later version, with the
referral block folded into it, and `drafts/referral-outcome.html` is the short follow-up
that took the place of the standalone referral form. The parked pair supersedes the root
pair in design, but it supersedes it in use only once the per-organisation locked house
exists. Until then the root files stay as they are, and this folder is the record of where
the design went.

`service-point.html` and `provider-register.html` were never on main. They enter the
repository here for the first time.

## The merged pair is now the only design for contacts and referrals

Decision of 23 September, confirmed on 12 October. A referral is an outcome of a
contact, not a parallel event, so the two are one form: `contact.html` here carries
the referral as its last section, opened only when a referral was made. The person
is typed once and carries one code.

`referral-outcome.html` stays a form of its own on purpose. The outcome is known
days later, often by a different worker or the receiving organisation, so folding it
in would mean either editing a saved record or holding a form open for days. It is
keyed by the contact code; one row is one referral outcome.

The standalone `contact.html` and `referral.html` that stood at the repository root
were the versions of 21 September, from before that decision. They have been
removed, together with the two cards on the Layer 1 landing page and the two entries
in the translation preview index. Nothing person-level is offered anywhere until the
per-organisation locked house exists and the written basis from EDCD and the TWG is
in hand -- the decision of 11 October.

The PHQ-9 page linked to the deleted referral form from its item-9 instruction, at
the point where a positive answer on thoughts of self-harm is handled. That line now
names the organisation's own referral pathway instead of a form, so the instruction
still stands and no link is dead.
