#!/usr/bin/env python3
"""Test stage answers and sequential combinations against SMALL_B64, INNER_B64, and COSMIC_B64."""
import sys, itertools
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from systematic_solver import run_sweep

stage_answers = [
    'theseedisplanted',
    'theflowerblossomsthroughwhatseemstobeaconcretesurface',
    'causality',
    'safenetlunahsm11110',
    'jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple',
    'thematrixhasyou',
    'incaseyoumanagetocrackthistheprivatekeysbelongtohalfandbetterhalfandtheyalsoneedfundstolive',
    'halfandbetterhalf',
    'betterhalf',
    'half',
    'matrixsumlist',
    'lastwordsbeforearchichoice',
    'thispassword',
    'ourfirsthintisyourlastcommand',
    'enter',
    'yinyang',
    'cosmicduality',
    'salphaseion',
    'hashthetext',
    'GSMGIO5BTCPUZZLECHALLENGE1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe',
    '1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe',
    '17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa'
]

cands = set(stage_answers)

# Sequential prefix chains
for i in range(2, 6):
    cands.add(''.join(stage_answers[:i]))
    cands.add(' '.join(stage_answers[:i]))

# SalPhaseIon specific token chains
salph_tokens = ['matrixsumlist', 'lastwordsbeforearchichoice', 'thispassword', 'ourfirsthintisyourlastcommand', 'enter']
for L in range(2, len(salph_tokens) + 1):
    for perm in itertools.permutations(salph_tokens, L):
        cands.add(''.join(perm))
        cands.add(' '.join(perm))

# Pairs of all stage answers
for s1, s2 in itertools.permutations(stage_answers, 2):
    cands.add(s1 + s2)
    cands.add(s1 + ' ' + s2)
    cands.add(s1 + '\n' + s2)

print(f'Total candidates: {len(cands)}')
run_sweep(list(cands), 'STAGE_COMBINATIONS')
