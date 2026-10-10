#!/bin/bash
# detached: remaining engine corpora through fastcheck (AES) with 2 procs, niced
cd /home/vin/bitcoin_puzzle/scratch
for f in engine_puzzle_texts engine_creator_messages engine_gsmg_public_site engine_carroll_public_domain engine_chat_substantive_part3 engine_chat_substantive_part4; do
  if [ -f wf/$f.txt ]; then
    echo "=== $f $(date)" >> wf/detached_engine.log
    nice -n 10 python3 fastcheck.py --file wf/$f.txt --procs 2 --label detached_$f >> wf/detached_engine.log 2>&1
  fi
done
echo "=== ALL DONE $(date)" >> wf/detached_engine.log
