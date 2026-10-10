#!/bin/bash
# Waits for run_engine_small.sh, then fastcheck on chat remainder (part3+part4 = 5..8-word windows of main lines 890001..end),
# then deadline-guarded brainwallet runs (bw_fast = bw_oracle derivations, multiprocess) on files never covered by bw.
cd /home/vin/bitcoin_puzzle/scratch
S=wf/run_engine_chain2.status
while ! grep -q ALLDONE wf/run_engine_small.status; do sleep 20; done
echo "START chat_rest $(date +%T)" >> $S
python3 fastcheck.py --file wf/engine_chat_substantive_rest.txt --procs 3 --label engine_chat_substantive_rest > wf/fastcheck_engine_chat_substantive_rest.log 2>&1
echo "END chat_rest rc=$? $(date +%T)" >> $S
DEADLINE=$(date -d "13:50" +%s)
run_bw () { # label file mode derivs extra
  now=$(date +%s); left=$(( DEADLINE - now )); if [ $left -lt 120 ]; then echo "SKIP $1 (past deadline) $(date +%T)" >> $S; return; fi
  echo "START $1 $(date +%T) budget=${left}s" >> $S
  timeout ${left}s python3 wf/bw_fast.py --file $2 --label $1 --procs 3 --mode $3 --derivs $4 $5 > wf/$1.log 2>&1
  echo "END $1 rc=$? $(date +%T)" >> $S
}
run_bw bw_engine_gsmg_public_site_reduced wf/engine_gsmg_public_site.txt reduced "sha256,sha256d,sha256(hex),hex-as-key" ""
run_bw bw_engine_carroll_public_domain_alnum wf/engine_carroll_public_domain.txt alnum "sha256" ""
run_bw bw_engine_chat_substantive_alnum_w5 wf/engine_chat_substantive.txt alnum "sha256" "--max-words 5"
echo "ALLDONE $(date +%T)" >> $S
