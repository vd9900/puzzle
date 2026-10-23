import json,os
D='/home/vin/bitcoin_puzzle/scratch/c39/docs1/'
parts={k:json.load(open(D+'part_%s.json'%k)) for k in 'ABCDE'}
cat=[];leads=[];cm=[]
for k,p in parts.items():
    for c in p['catalog']: c['part']=k; cat.append(c)
    for l in p['leads']: l['part']=k; leads.append(l)
    for m in p.get('creator_message_claims',[]): m['part']=k; cm.append(m)
g1=[ln.split('\t')[0].replace('docs/','',1) for ln in open('/home/vin/bitcoin_puzzle/data/user_supplied/telegram/docs/GROUP1.txt') if ln.strip()]
have={c['path'] for c in cat}
missing=[p for p in g1 if p not in have]; extra=[p for p in have if p not in g1]
# verification annotations from own independent checks (2026-10-13)
V=[]
def ver(match_src, match_txt, note):
    n=0
    for l in leads:
        if match_src in l['source'] and match_txt.lower() in (l['claim']+json.dumps(l.get('exact_strings',''))).lower():
            l['own_check']=note; n+=1
    V.append(dict(target=match_src+' :: '+match_txt, note=note, leads_annotated=n))
ver('reproduce_all_bulbs_verified_stage2753',"'Chain1'","REPRODUCED independently with openssl CLI (AES-256-CBC, -md md5, raw passphrase) on research/artifacts/salphaseion-small.b64: last byte 0x01 -> 79 B, sha256 1449a217...26bf matches; output is binary (printable fraction 0.38 ~ random). Not self-verifying: wrong keys give 0x01 pad 1/256; script itself shows a 2nd passing preimage.")
ver('reproduce_all_bulbs_verified_stage2753',"'Chain2'","REPRODUCED independently: uncompressed WIF(chain1[:32]) (5K2byJ...) as openssl -md md5 passphrase on research/artifacts/phase32-inner.b64 -> 0x01 pad, 79 B, sha256 b40fce72...d004 matches; binary output (printable 0.42). Tail chain2[64:79]=740a25de4b8e946d0a5ae2667a23a2 = the 'E_S gate' value in dbbib-faed-analysis. Conditional chance ~1/256 per derivation tried; not self-verifying.")
ver('dbbib-faed-analysis',"RAW_PW","Same as Chain1/Chain2 (reproduced). Salt 3ab585348552415d = SalPhaseIon small blob; salt b45a5e3d827593ca = known Phase 3.2 inner blob (research/artifacts/phase32-inner.b64), so the 'p32' layer source is identified.")
ver('2020-301.pdf',"MadHatter","CLOSED by own check (mycheck/madhatter_check.py): MadHatter ciphertext needs every 4-symbol block to have 4 distinct letters; faed has 83-88 of 142 blocks with repeats at every offset 0-3 (dbbi 14-17/22), and 570/91 are not multiples of 4. Not MadHatter.")
ver('dbbi_sum_faed.py',"upper triangle","RAN own re-implementation (mycheck/quick_rowsum.py): S=JLIQFOPGVBLSENDTHECZAGJJYDSWCGUDJNFTWB (contains 'SENDTHE', rest gibberish), H=OLIQUBROVQLTOSETHEXQYOJSSICJFGUDCCVBWQ, L=JLUPFLPGLBLUENETDICZAGAJQDSWCGUDONFHWB. Ad-hoc decoder with many free choices -> look-elsewhere; not a solution.")
for l in leads:
    if l['part']=='A' and 'U2FsdGVkX1+0Wl49' in json.dumps(l):
        l['own_check']="Blob U2FsdGVkX1+0Wl49gnWTyiim... is the known Phase 3.2 inner blob (research/artifacts/phase32-inner.b64); 'plaintext' claim refuted (it is openssl Salted__ ciphertext)."
top10=[
 dict(rank=1,lead="Chain1->Chain2: SalPhaseIon small blob + 'matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist' (MD5 KDF) -> 79 B; WIF(first 32 B) opens Phase 3.2 inner blob -> 79 B (E_S=740a25de4b8e946d0a5ae2667a23a2)",sources=["reproduce_all_bulbs_verified_stage2753.py","dbbib-faed-analysis-2026-10-10.md","salphaseion_plain_79.bin (different 79-B hit)"],checkable="yes",status="independently reproduced; both are single-byte 0x01 pads with random-looking binary output -> consistent with padding false positives found by search; cheap self-verifying follow-up: K_C1/K_C2/K_S1/K_S2 as privkeys vs prize address (My2cents reports EC combos negative)"),
 dict(rank=2,lead="Chain3 'cosmic_correct': Cosmic Duality blob (1328-B ct) with raw 32-B pass = XOR of sha256 of 7 tokens (a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735), MD5 KDF -> 1327 B (0x01 pad)",sources=["reproduce_all_bulbs_*.py","My2cents_.md","GSMG_research_baseline.md"],checkable="yes",status="one decrypt; not self-verifying (1/256); token subset chosen post hoc; maintainer called it a false positive"),
 dict(rank=3,lead="'12 addresses' / 39 'extra door' P2PKH addresses = Base58Check(00||CC[32X+16:32X+32]||BE32(X)) over Chain3 output",sources=["12-addresses.txt","from_issue110_addresses.py"],checkable="partial",status="Base58Check validity is by construction (no evidence); reported empty on-chain; depends on disputed Chain3"),
 dict(rank=4,lead="Chain4: chain3[158:1326] XOR 8-byte mask b657264f2f6e6921 -> 'Salted__' -> decrypt 1151 B",sources=["reproduce_all_bulbs_corrected.py"],checkable="yes",status="mask is chosen to make 'Salted__' (zero evidence); 0x01 pad again"),
 dict(rank=5,lead="'Half'/'Better Half' via 103x103 matrix on Chain3 output (addresses 1JG648ya..., 145ZQ9si...)",sources=["My2cents_.md","GSMG_research_baseline.md"],checkable="partial",status="author grades it unauthenticated; EC combos vs prize key negative"),
 dict(rank=6,lead="E_S 'gate': find X with sha256(X)[:30 hex]==740a25de4b8e946d0a5ae2667a23a2",sources=["dbbib-faed-analysis-2026-10-10.md"],checkable="partial",status="a match would self-verify (120 bits) but needs guessing X and presupposes Chain2 is real; >8.3M windows already negative per author"),
 dict(rank=7,lead="Medicine hint: two lowercase 'rx' in the 1,539-char Phase 3.2.1 intermediate at 68 and 1237 (distance 1169); Beaufort plaintext at 1169 begins 'ciphers'",sources=["GSMG_research_baseline.md"],checkable="yes",status="deterministic on solved text; interpretive, no oracle"),
 dict(rank=8,lead="MadHatter (ePrint 2020/301, A-I ciphertext, two plaintexts) as the SalPhaseIon a-i cipher",sources=["2020-301.pdf"],checkable="yes",status="CLOSED by own check: faed/dbbi blocks repeat letters at every offset"),
 dict(rank=9,lead="dbbi as upper triangle of symmetric 14x14 (91=C(14,2)) -> row sums XOR faed 15-wide row sums mod 26",sources=["dbbi_sum_faed.py"],checkable="yes",status="ran: 'SENDTHE' fragment in gibberish; look-elsewhere; triangle idea already in research/evidence/cycle02"),
 dict(rank=10,lead="17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa: 'dualite gate' (dbbib file) vs self-transfer (My2cents)",sources=["dbbib-faed-analysis-2026-10-10.md","My2cents_.md"],checkable="partial",status="on-chain history check only; no derivation that would self-verify"),
]
out=dict(generated="2026-10-13",scope="GROUP1 (117 docs) of user_supplied/telegram/docs",
  method="4 parallel read-only subagents (parts A-D) + own pass (part E); no data-file code executed; own checks in docs1/mycheck/",
  coverage=dict(group1_count=len(g1),catalog_count=len(cat),missing=missing,extra=extra),
  notes=["No document in GROUP1 mentions 'BYTENPHASE'.",
         "All creator/admin quotes found (Jrk_Bgrt_Chat_History, messages.zip export, baseline, My2cents) already exist in research/ or scratch/ notes; no new creator hint text found.",
         "Known official blobs present as copies: Phase 2 (ph2_aes_1), Phase 3 (ph3_aes_2), Phase 3.2 inner (ph3_aes_3), SalPhaseIon small (extra_aes_1), Cosmic Duality (salph.html)."],
  own_checks=V, top10_checkable=top10, catalog=cat, leads=leads, creator_message_claims=cm)
json.dump(out,open(D+'leads.json','w'),indent=1,ensure_ascii=False)
print('catalog',len(cat),'leads',len(leads),'creator',len(cm),'missing',missing,'extra',extra,[ (v['target'][:40],v['leads_annotated']) for v in V])
