#!/bin/bash
# Sequential fastcheck over the four small corpora, priority order, per-corpus logs.
cd /home/vin/bitcoin_puzzle/scratch
for c in puzzle_texts creator_messages gsmg_public_site carroll_public_domain; do
  echo "START $c $(date +%T)" >> wf/run_engine_small.status
  python3 fastcheck.py --file wf/engine_$c.txt --procs 3 --label engine_$c > wf/fastcheck_engine_$c.log 2>&1
  echo "END $c rc=$? $(date +%T)" >> wf/run_engine_small.status
done
echo "ALLDONE $(date +%T)" >> wf/run_engine_small.status
