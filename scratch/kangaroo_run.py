#!/usr/bin/env python3
"""Run JeanLucPons Kangaroo over candidate intervals. Usage:
  python3 kangaroo_run.py --selftest
  python3 kangaroo_run.py --ranges kangaroo/ranges.json [--maxbits 72] [--threads 4]
Any found key is written ONLY to scratch/wf/HITS.log and kangaroo/FOUND_<name>.txt (never printed)."""
import json, subprocess, sys, os, time, argparse, re, hashlib, random
sys.path.insert(0,'/home/vin/bitcoin_puzzle')
from tools.gsmg import CURVE_ORDER as N, candidate_addresses, TARGET_ADDRESS
from cryptography.hazmat.primitives.asymmetric import ec
KANG='/home/vin/bitcoin_puzzle/scratch/kangaroo/Kangaroo/kangaroo'
PUB_UNC='04f4d1bbd91e65e2a019566a17574e97dae908b784b388891848007e4f55d5a4649c73d25fc5ed8fd7227cab0be4e576c0c6404db5aa546286563e4be12bf33559'
def compress(unc):
    x=unc[2:66]; y=int(unc[66:],16); return ('03' if y&1 else '02')+x
PUB=compress(PUB_UNC)
def run(start,end,pub,threads,timeout,tag):
    inf=f'/tmp/kang_{tag}.txt'
    open(inf,'w').write(f'{start:x}\n{end:x}\n{pub}\n')
    t0=time.time()
    try:
        p=subprocess.run(['nice','-n','10',KANG,'-t',str(threads),'-m','3',inf],capture_output=True,text=True,timeout=timeout)
        out=p.stdout+p.stderr
    except subprocess.TimeoutExpired as e:
        out=(e.stdout or b'').decode() if isinstance(e.stdout,bytes) else (e.stdout or '')
        return None,time.time()-t0,'TIMEOUT'
    m=re.search(r'Priv:\s*0x([0-9A-Fa-f]+)',out)
    return (int(m.group(1),16) if m else None),time.time()-t0,out[-400:]
def selftest(threads):
    k=random.SystemRandom().randrange(2**44,2**45)
    pubn=ec.derive_private_key(k,ec.SECP256K1()).public_key().public_numbers()
    pub=('03' if pubn.y&1 else '02')+f'{pubn.x:064x}'
    found,dt,log=run(2**44,2**45-1,pub,threads,600,'selftest')
    print(f'selftest 2^44 range: found={found==k} in {dt:.1f}s'); 
    if found!=k: print(log)
    return found==k
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--selftest',action='store_true'); ap.add_argument('--ranges'); ap.add_argument('--maxbits',type=int,default=72); ap.add_argument('--threads',type=int,default=4); ap.add_argument('--only',default='')
    a=ap.parse_args()
    if a.selftest: sys.exit(0 if selftest(a.threads) else 1)
    rs=json.load(open(a.ranges))
    import glob
    done=set()
    for lf in glob.glob('/home/vin/bitcoin_puzzle/scratch/kangaroo/run_*.log'):
        lines=open(lf).read().split('\n')
        for i,l in enumerate(lines):
            if l.startswith('[') and i+1<len(lines) and 'no key in interval' in lines[i+1] and 'TIMEOUT' not in lines[i+1]:
                done.add(l.split(']',1)[1].split('bits=')[0].strip())
    print('skipping',len(done),'completed intervals')
    rs=[r for r in rs if r['name'] not in done]
    for r in rs:
        if r['bits']>a.maxbits: continue
        if a.only and a.only not in r['name']: continue
        start=int(r['start'],16); end=int(r['end'],16)
        bits=(end-start).bit_length()
        # expected ops ~ 2*sqrt(range); allow generous timeout: assume >= 5M ops/s
        exp_ops=2*(2**(bits/2)); timeout=max(300,int(exp_ops/0.25e6*4)+120)
        print(f'[{time.strftime("%H:%M:%S")}] {r["name"]:48s} bits={bits:3d} timeout={timeout}s',flush=True)
        found,dt,log=run(start,end,PUB,a.threads,timeout,'main')
        if found:
            ads=candidate_addresses(found.to_bytes(32,'big'))
            ok=TARGET_ADDRESS in ads.values()
            print(f'   !!! KANGAROO RESULT after {dt:.0f}s; address match={ok}',flush=True)
            if ok:
                open(f'/home/vin/bitcoin_puzzle/scratch/kangaroo/FOUND_{re.sub("[^A-Za-z0-9]","_",r["name"])}.txt','w').write(f'{found:064x}\n')
                open('/home/vin/bitcoin_puzzle/scratch/wf/HITS.log','a').write(json.dumps({'type':'KANGAROO_SOLVE','range':r['name']})+'\n')
                print('   SOLVED — key written to kangaroo/FOUND_*.txt (not printed)'); return
        else:
            print(f'   no key in interval ({dt:.0f}s) {"TIMEOUT" if log=="TIMEOUT" else ""}',flush=True)
if __name__=='__main__': main()
