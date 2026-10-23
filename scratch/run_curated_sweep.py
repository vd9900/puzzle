#!/usr/bin/env python3
"""Run infallible systematic oracle across all curated candidate files in scratch/wf."""
import sys, os, time, re
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from systematic_solver import run_sweep

CAND_FILES = [
    'cands_lens_architect_choice.txt',
    'cands_lens_architect_choice_2.txt',
    'cands_lens_architect_choice_forms.txt',
    'cands_lens_architect_choice_1141.txt',
    'cands_lens_books_sources.txt',
    'cands_lens_books_sources_2.txt',
    'cands_lens_books_sources_3.txt',
    'cands_lens_creator_context.txt',
    'cands_lens_creator_context_pagetext.txt',
    'cands_lens_mr_robot_table.txt',
    'cands_lens_mr_robot_table_2.txt',
    'cands_lens_web_osint.txt',
    'cands_lens_parse_skeptic.txt',
    'cands_chunk00.txt',
    'cands_chunk01.txt',
    'cands_chunk02.txt',
    'cands_chunk03.txt',
    'cands_chunk04.txt',
]

def load_file(fname):
    path = os.path.join('/home/vin/bitcoin_puzzle/scratch/wf', fname)
    if not os.path.exists(path):
        return []
    cands = []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Remove any trailing tab-separated provenance tag if present
            if '\t' in line:
                line = line.split('\t')[0].strip()
            if line:
                cands.append(line)
    return cands

def main():
    print('Starting curated candidate sweep...')
    t_start = time.time()
    total_cands = 0
    total_hits = 0
    
    for fname in CAND_FILES:
        cands = load_file(fname)
        if not cands:
            continue
        label = fname.replace('.txt', '').replace('cands_', '')
        print(f'\n--- Running {label} ({len(cands)} candidates) ---')
        hits = run_sweep(cands, label=label)
        total_cands += len(cands)
        total_hits += len(hits)
        
    dt = time.time() - t_start
    print(f'\n======================================================')
    print(f'Sweep complete in {dt:.1f}s. Total files: {len(CAND_FILES)}, cands: {total_cands}, hits: {total_hits}')

if __name__ == '__main__':
    main()
