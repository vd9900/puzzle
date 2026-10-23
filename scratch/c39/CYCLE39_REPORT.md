# Cycle 39 — full Telegram group review (2026-10-13)

Status: UNSOLVED. Inputs (user-supplied, git-ignored under data/user_supplied/telegram/): two Telegram Desktop HTML exports of
"GSMG Puzzle Solvers" (63,040 messages, 2019-04-20 .. 2026-10-12), 2,869 images (OCR'd on the VM, images then deleted there),
235 unique shared documents (converted to text; nothing executed). Tools: tools/tg_html_parse.py, tools/docs_to_text.py.
Per-lens leads: scratch/c39/{chunk0..5,creator,docs0,docs1,ocr}/leads.json (+confirmations.json).

## Creator corpus
- 492 creator messages (old corpus had 411); 81 new, 65 from Jul/Sep 2026. No technical hint in them. Key statements:
  SalPhaseIon "100% solvable" (re-verified after the givetit fix); "My close friends have the best chance of solving it ...
  NOTE: that is a hint"; "Some already found it. And understood not to risk it"; answer on a "hidden laptop ... in a room with
  a hidden door"; "the url (and thus the original puzzle) is gone"; 🤐 on whether dbbi/faed are decodable; "Pfff. Coincidence."
  to the YOUWON/103-digit idea; 👆 after the SalPhaseIon-capitalization question points to a DELETED message (#70314).
- Creator media ever posted: 3 photos (dessert scene, Decentraland hint, a 2026 drug screenshot) — no new hint images.
- Recovered from screenshots (not in export): DM 2021-03-15 "Same software was used in every phase" (=> unsolved blobs use the
  solved phases' openssl setup; MD5-KDF "chains" are wrong) and SalPhaseIon hint "obviously the thing hush hush doesn't mention"
  (= the text on the first image, i.e. the known HASHTHETEXT entrance). The "caesar -> removethecorrecthinttoproceedtothenextstage
  -> esrever -> 2nd binary part" message is about GSMG's separate 2019 April-1st "rickroll" puzzle, not the unsolved stages.
- Confirmations/denials table (143 responses, 53 structural statements): scratch/c39/creator/confirmations.json. Notables: inner
  3.2 blob undecrypted ("Correct") and NOT the SalPhaseIon hint ("No."); blockchain OP_RETURN messages not his ("Correct",
  2023-08-29); {1},{4},{21} door hint = April Fools; "Salvation passed: Partly"; "no internet needed / you have all the info".

## Community 2026 (12,582 messages) + documents + screenshots
- No verified progress beyond the known state. Every claimed decrypt (Chain 1-4 / cosmic_correct / "12" (39) addresses,
  Marc's chain, ZION, test151, adipfBrr, Cebotari) is a padding false positive (~1/256 per wrong password; can be manufactured),
  fabricated LLM output, or unreproducible. Posted keys do not give the prize address.
- gsmg.io lapsed in 2026 and is now run by a third party: its new pages, game, "finalGrid", emails from admin@, a Jan-2026 blob
  are NOT creator material. Our cycle-36 live-site probes may have hit the new owner's copy.
- btcseed closed again by community nulls (forced Bifid geometry; BIP39 hits at chance).
- dbbi "64 tokens / 16 symbols = substituted SHA-256 digest" (MrNobody, PROGRESS.md): look-elsewhere shuffle p=0.011, but under
  the fair null that preserves the known prime-marker layout it occurs 12-13% of the time => artifact (scratch/c39/hexshape/).
- 103-letter SalPhaseIon instruction string ends on the FEFEFE cell when laid row-major (cell 103): letters under blue/yellow
  cells read 'xtfosonn' / 'lhaoe' — coincidence.
- phase3.1_old.aes = original 2019 Phase 3.2 blob; decrypts with the givetit password to the identical plaintext (nothing hidden).

## Conclusion
Seven years of group discussion, all shared documents and all screenshots contain no hidden hint or verified intermediate that
moves past the known frontier (dbbi prime-marker layer understood; residual/faed/matrixsumlist semantics unknown). The creator's
2026 statements point to personal knowledge ("close friends") as the missing ingredient, which this project does not research.
