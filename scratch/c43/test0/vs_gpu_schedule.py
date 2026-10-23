"""c43 test0: finish the VanitySearch planted-seed test (GPU schedules), derivation-backed, perfect oracle.

Derivation (VanitySearch source read at tags 1.0 .. 1.15, all 2019 releases; see vs_version_check.txt):
  start key S = int_le(sha256(pbkdf2_hmac_sha512(seed, 'VanitySearch', 2048, 64)))  -- identical in every 2019 tag
      (confirmed byte-for-byte by compiling the tool's own hash/sha512.cpp + sha256.cpp from tags 1.0 and 1.15)
  CPU thread t        : S + t<<64 + j                              (all tags)            [already run: t<64, j<2^30]
  GPU sched A (1.5+)  : S + i<<80 + (0x80+g)<<112 + j              (g = index in -gpuId list)
  GPU sched B (1.0-1.4): S + i<<96 + j                             (single GPU, no gpu term)
  found key = s * lambda^e * (S + off + j) mod n,  e in {0,1,2}, s = +-1  (endo/sym; superset for early tags)
  rekey: absent before 1.11, default 0 (disabled) in 1.11-1.15 -> deterministic schedule.
  Default GPU threads = 1024 * (#SM) in every tag (16*MP x 64 in 1.0-1.5, 8*MP x 128 later) -> i < 2^17 covers <=128 SMs.
Search: BSGS on x-coordinates. Per (seed, schedule, g, e, s): Q_i = s*lambda^-e*P - (S + off_i)G, j = dlog(Q_i) in [0, 2^22+2^21).
Oracle: full point (s*lambda^e*(S+off+j))G == prize pubkey 04f4d1bb... (no false positives possible).
Usage: python3 vs_gpu_schedule.py [nworkers]
"""
import sys, os, time, hashlib, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ec
N = ec.N
BABY = 1 << 21; STRIDE = 1 << 22; NCS = 2          # j in [0, STRIDE*NCS - BABY]... covers [0, 2^22 + 2^21]
JMAX = STRIDE * (NCS - 1) + BABY
NTHR = 1 << 17
M64 = (1 << 64) - 1

def vs_start(seed):
    return int.from_bytes(hashlib.sha256(hashlib.pbkdf2_hmac('sha512', seed.encode(), b'VanitySearch', 2048, 64)).digest(), 'little')

# start keys produced by the tool's OWN C++ hash code (tags 1.0 and 1.15 compiled identically; vs_hash/startkey_*)
CPP_START = {
    'controlseed': 0x0e2897a739e49e7daf804b7c442cfeb7278f2ccf8cbae92da547657c29a00a7c,
    'theseedisplanted': 0x25f8b0c9de1f20c4a0a63081acab5198c4296b3893839b76e76307da7a5b8c29,
    'gsmg.io/theseedisplanted': 0xd3fd9e811186566100b807506080b7d27daec83da5b2bfc528af96a2306b1f80,
    '6e3f5a7baf924d8546f5f7af94a43b8424e3c810983f9795eb8451ad4243d860': 0x075bd785fb3cf26cf792f7c37682d877d0e0018516f6e4e566f763731807342c,
    '3a3f0e245360d51ea41f55c7db8a13f270fbf3dcef3b4f94ac1c4b3cee8db2e9': 0xf4a49174c7e4189531e197e0e3a5de3b87b8e53b65d69fc58d1eafbf6ccea4ee,
}
for sd, v in CPP_START.items():
    assert vs_start(sd) == v, sd

SCHED = {  # name: (base offset fn(g), thread shift)
    'cpu':  (lambda g: 0, 64),
    'gpuA': (lambda g: (0x80 + g) << 112, 80),
    'gpuB': (lambda g: 0, 96),
}

TAB = {}
def build_table():
    pt = None
    for j in range(1, BABY + 1):
        pt = ec.add(pt, ec.G); TAB[pt[0] & M64] = j

STRIDE_NEG = None
def task(args):
    """args = (label, S, sched, g, e, s, tmax, ncs, target). Returns list of verified hits."""
    label, S, sched, g, e, s, tmax, ncs, target = args
    base_fn, sh = SCHED[sched]
    base = base_fn(g)
    T = ec.mul(s * pow(ec.LAM, -e, N) % N, target)            # = (S + base + t<<sh + j) G
    Q = ec.add(T, ec.neg(ec.mul(S + base)))
    step = ec.neg(ec.mul(1 << sh))
    sneg = ec.neg(ec.mul(STRIDE))
    hits = []
    for t in range(tmax):
        R = Q
        for c in range(ncs):
            cands = []
            if R is None: cands = [c * STRIDE]
            else:
                jj = TAB.get(R[0] & M64)
                if jj is not None: cands = [c * STRIDE + jj, c * STRIDE - jj]
            for j in cands:
                if j < 0: continue
                k = s * pow(ec.LAM, e, N) * (S + base + (t << sh) + j) % N
                if ec.mul(k) == target:
                    hits.append(dict(label=label, sched=sched, g=g, e=e, s=s, t=t, j=j))
            if c + 1 < ncs: R = ec.add(R, sneg)
        Q = ec.add(Q, step)
    return hits

def full_tasks(label, S, target, nthr=NTHR):
    out = []
    for e in range(3):
        for s in (1, -1):
            out.append((label, S, 'gpuA', 0, e, s, nthr, NCS, target))
            out.append((label, S, 'gpuA', 1, e, s, nthr, NCS, target))
            out.append((label, S, 'gpuB', 0, e, s, nthr, NCS, target))
    return out

if __name__ == '__main__':
    nw = int(sys.argv[1]) if len(sys.argv) > 1 else os.cpu_count()
    t0 = time.time(); build_table(); print(f'baby table {len(TAB)} entries, {time.time()-t0:.1f}s; j window [0,{JMAX}] (2^{JMAX.bit_length()-1}+), threads<{NTHR}', flush=True)
    L = ec.LAM
    sh = lambda x: hashlib.sha256(x.encode()).hexdigest()
    SEEDS = ['theseedisplanted', 'gsmg.io/theseedisplanted', sh('theseedisplanted'), sh('gsmg.io/theseedisplanted')]
    for sd in SEEDS + ['controlseed']:
        assert vs_start(sd) + (1 << 121) < N                   # no 2^256 / n wrap inside the schedule
    # ---- positive controls: (task, expected (sched,g,e,s,t,j))
    Sc = vs_start('controlseed')
    ctrl = []
    k = (-pow(L, 2, N) * (Sc + (5 << 64) + 0x2345678)) % N                 # old planted CPU key
    ctrl.append((('ctl_cpu_planted', Sc, 'cpu', 0, 2, -1, 8, 10, ec.mul(k)), ('cpu', 0, 2, -1, 5, 0x2345678)))
    k = (Sc + (777 << 80) + (0x80 << 112) + 123456) % N                    # old planted GPU key
    ctrl.append((('ctl_gpuA_planted', Sc, 'gpuA', 0, 0, 1, 800, NCS, ec.mul(k)), ('gpuA', 0, 0, 1, 777, 123456)))
    k = (-L * (Sc + (100000 << 96) + 3 * (1 << 20) + 5)) % N               # NEW schedule B, edge-ish thread/j
    ctrl.append((('ctl_gpuB_planted', Sc, 'gpuB', 0, 1, -1, 100001, NCS, ec.mul(k)), ('gpuB', 0, 1, -1, 100000, 3 * (1 << 20) + 5)))
    k = (pow(L, 2, N) * (Sc + (NTHR - 1 << 80) + (0x81 << 112) + JMAX - 1)) % N   # last thread, GPU 1, top of j window
    ctrl.append((('ctl_gpuA_edge', Sc, 'gpuA', 1, 2, 1, NTHR, NCS, ec.mul(k)), ('gpuA', 1, 2, 1, NTHR - 1, JMAX - 1)))
    # planted inside a REAL seed's schedule (exercises the exact real-seed path)
    Sr = vs_start('gsmg.io/theseedisplanted')
    k = (-(Sr + (31337 << 96) + 2048)) % N
    ctrl.append((('ctl_realseed_gpuB', Sr, 'gpuB', 0, 0, -1, 31338, NCS, ec.mul(k)), ('gpuB', 0, 0, -1, 31337, 2048)))
    # REAL VanitySearch outputs from the author's README (base key printed by the tool, found key printed by the tool)
    b0 = 0x3C5539728405D2FB5DE38E807C97340FDA1EDA6A3D8F37CFAABC1EE85993660; k0 = 0x3C5539728405D2FB5DE38E807C97340FDA1EDA6A3D8F381FAABC1EE85D6E9D6
    ctrl.append((('ctl_readme_v1.0_cpu', b0, 'cpu', 0, 0, 1, 8, NCS, ec.mul(k0)), ('cpu', 0, 0, 1, 5, 4043638)))
    b1 = 0x87B1EC7916A180ACCF07CAAEFA7F6508F3898F61AF49C201D70DF1543CCBA572; k1 = 0xF36DD1EEC2A9658E50B39B280D4002ED3A07C7B6C07B37B191973BDDFBF9E375
    ctrl.append((('ctl_readme_v1.11_gpu', b1, 'gpuA', 0, 1, -1, 5000, NCS, ec.mul(k1)), ('gpuA', 0, 1, -1, 0x1283, 58797)))
    assert ec.addr(ec.mul(k1), True) == '1TryMeTKr3tuJZYHMSNWdPZfhRRNYj3yE'          # README v1.11 pub addr
    assert ec.addr(ec.mul(k0), True) == '1Testa3r7d1FF4o5pbWYiUSqBdMWMq9MY'          # README v1.0 pub addr
    # ---- real run + matched negative control (non-derived seed 'controlseed', identical tasks, real target)
    real = []
    for sd in SEEDS: real += full_tasks('REAL:' + sd[:24], vs_start(sd), ec.TGT)
    neg = full_tasks('NEGCTL:controlseed', Sc, ec.TGT)
    ctx = mp.get_context('fork')
    with ctx.Pool(nw) as pool:
        t1 = time.time()
        res = pool.map(task, [c[0] for c in ctrl], chunksize=1)
        ok = True
        for (tk, exp), hits in zip(ctrl, res):
            got = [(h['sched'], h['g'], h['e'], h['s'], h['t'], h['j']) for h in hits]
            good = exp in got
            ok &= good
            print(f'{tk[0]:24s} expected={exp} got={got} {"OK" if good else "FAIL"}', flush=True)
        print(f'controls {"ALL OK" if ok else "FAILED"} ({time.time()-t1:.0f}s)', flush=True)
        if not ok: sys.exit(1)
        t1 = time.time()
        allt = real + neg
        hits_all = []
        for i, h in enumerate(pool.imap(task, allt, chunksize=1)):
            hits_all += h
            if (i + 1) % 18 == 0: print(f'  {i+1}/{len(allt)} tasks done ({time.time()-t1:.0f}s), hits so far {len(hits_all)}', flush=True)
        print(f'real+negctl tasks: {len(allt)} ({len(real)} real, {len(neg)} neg), threads/task={NTHR}, '
              f'point-ops~{len(allt)*NTHR*(NCS+0)/1e6:.1f}M, {time.time()-t1:.0f}s', flush=True)
        real_hits = [h for h in hits_all if h['label'].startswith('REAL')]
        neg_hits = [h for h in hits_all if h['label'].startswith('NEGCTL')]
        print(f'REAL hits: {len(real_hits)}', flush=True)
        print(f'NEGCTL hits: {len(neg_hits)}', flush=True)
        if real_hits:
            print('HIT (details withheld; see HITS.log)')
            with open(os.path.join(HERE, 'HITS_local.log'), 'a') as f:
                for h in real_hits: f.write(repr({k: v for k, v in h.items()}) + '\n')
