#!/usr/bin/env python3
"""Sweep candidates from 'Le Miroir de la vie et de la mort' (Cosmic Duality p. 39 engraving,
Rijksmuseum RP-P-OB-74.874: 'Buste van een half skelet en een half jonge vrouw').
Tests French poem, Latin maxims, Dutch titles, and English translations against
all three blobs (small, inner, cosmic) under sha256 and md5 EVP KDFs,
checking both printable plaintext and target address private key matches.
"""
import sys, os, time, re, json
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from systematic_solver import run_sweep

FRENCH_LINES = [
    "Mondains qui faictes cas des beautez d'un visage",
    "Scachez, que les aymer ce n'est pas estre sage",
    "Puis que le temps enfin les doibt faire perir",
    "Nous n'avons icy bas chose aucune asseurée",
    "Tout change et nostre vie a si peu de durée",
    "Qu'en commençant à vivre on commence à mourir",
    # Modernized spelling
    "Mondains qui faites cas des beautés d'un visage",
    "Sachez, que les aimer ce n'est pas être sage",
    "Puisque le temps enfin les doit faire périr",
    "Nous n'avons ici bas chose aucune assurée",
    "Tout change et notre vie a si peu de durée",
    "Qu'en commençant à vivre on commence à mourir",
    # Without accents
    "Mondains qui faictes cas des beautez dun visage",
    "Scachez, que les aymer ce nest pas estre sage",
    "Puis que le temps enfin les doibt faire perir",
    "Nous navons icy bas chose aucune asseuree",
    "Tout change et nostre vie a si peu de duree",
    "Quen commencant a vivre on commence a mourir",
    "Mondains qui faites cas des beautes dun visage",
    "Sachez, que les aimer ce nest pas etre sage",
    "Puisque le temps enfin les doit faire perir",
    "Nous navons ici bas chose aucune assuree",
    "Tout change et notre vie a si peu de duree",
    "Quen commencant a vivre on commence a mourir",
    # Sub-phrases
    "commençant à vivre on commence à mourir",
    "commencant a vivre on commence a mourir",
    "on commence à mourir",
    "on commence a mourir",
    "commençant à vivre",
    "commencant a vivre",
    "les aymer ce n'est pas estre sage",
    "les aimer ce n'est pas être sage",
    "ce n'est pas estre sage",
    "ce n'est pas être sage",
    "chose aucune asseurée",
    "chose aucune assurée",
    "si peu de durée",
    "si peu de duree",
]

# Full stanzas / combined lines
STANZA_1 = "Mondains qui faictes cas des beautez d'un visage,\nScachez, que les aymer ce n'est pas estre sage,\nPuis que le temps enfin les doibt faire perir,\nNous n'avons icy bas chose aucune asseurée,\nTout change et nostre vie a si peu de durée,\nQu'en commençant à vivre on commence à mourir."
STANZA_2 = "Mondains qui faictes cas des beautez d'un visage, Scachez, que les aymer ce n'est pas estre sage, Puis que le temps enfin les doibt faire perir, Nous n'avons icy bas chose aucune asseurée, Tout change et nostre vie a si peu de durée, Qu'en commençant à vivre on commence à mourir."
STANZA_3 = "Mondains qui faictes cas des beautez d'un visage Scachez, que les aymer ce n'est pas estre sage Puis que le temps enfin les doibt faire perir Nous n'avons icy bas chose aucune asseurée Tout change et nostre vie a si peu de durée Qu'en commençant à vivre on commence à mourir"

TITLES = [
    "Le Miroir de la vie et de la mort",
    "Le Miroir de la vie, et de la mort",
    "LE MIROIR DE LA VIE ET DE LA MORT",
    "LE MIROIR DE LA VIE, ET DE LA MORT",
    "Le Miroir de la Vie et de la Mort",
    "Miroir de la vie et de la mort",
    "Miroir de la Vie et de la Mort",
    "Le Miroir de la vie",
    "Le Miroir de la mort",
    "Miroir de la vie",
    "Miroir de la mort",
    "Le Miroir",
    "Miroir",
]

LATIN = [
    "Res est forma fugax; quis sapiens bono confidat fragili",
    "Res est forma fugax, quis sapiens bono confidat fragili",
    "Res est forma fugax; quis sapiens bono confidat fragili?",
    "Res est forma fugax",
    "quis sapiens bono confidat fragili",
    "quis sapiens bono confidat fragili?",
    "bono confidat fragili",
    "forma fugax",
]

DUTCH = [
    "Buste van een half skelet en een half jonge vrouw",
    "Buste van een half skelet en half jonge vrouw",
    "Een half skelet en een half jonge vrouw",
    "Half skelet en half jonge vrouw",
    "half skelet en half jonge vrouw",
    "half skelet en een half jonge vrouw",
    "buste van een half skelet en een half jonge vrouw",
    "half skelet",
    "half jonge vrouw",
    "RP-P-OB-74.874",
    "RP-P-OB-74874",
    "Lugt 240",
    "René Guérineau",
    "Rene Guerineau",
    "Guérineau",
    "Guerineau",
]

ENGLISH = [
    "The Mirror of Life and Death",
    "Mirror of Life and Death",
    "The Mirror of Life and of Death",
    "Life and Death",
    "Life and death",
    "life and death",
    "To love beauty is not to be wise, for in the end time must destroy it",
    "To love beauty is not to be wise",
    "for in the end time must destroy it",
    "We have nothing certain down here, everything changes, and our life has so little duration that in beginning to live we begin to die",
    "We have nothing certain down here",
    "everything changes, and our life has so little duration that in beginning to live we begin to die",
    "and our life has so little duration that in beginning to live we begin to die",
    "that in beginning to live we begin to die",
    "in beginning to live we begin to die",
    "in beginning to live we begin to die.",
    "beginning to live we begin to die",
    "beginning to live on commence a mourir",
    "in beginning to live, we begin to die",
]

# Generate word n-grams from the poem
ALL_POEM_WORDS = "Mondains qui faictes cas des beautez dun visage Scachez que les aymer ce nest pas estre sage Puis que le temps enfin les doibt faire perir Nous navons icy bas chose aucune asseuree Tout change et nostre vie a si peu de duree Quen commencant a vivre on commence a mourir".split()
ngrams = []
for n in range(2, 7):
    for i in range(len(ALL_POEM_WORDS) - n + 1):
        ngrams.append(" ".join(ALL_POEM_WORDS[i:i+n]))

all_cands = set(FRENCH_LINES + [STANZA_1, STANZA_2, STANZA_3] + TITLES + LATIN + DUTCH + ENGLISH + ngrams)
print(f"Total unique candidates to sweep: {len(all_cands)}")

out_hits = run_sweep(list(all_cands), label="miroir_full_sweep")
print(f"Sweep completed. Structured hits: {len(out_hits)}")
if out_hits:
    for h in out_hits:
        print(f"HIT: {h}")
