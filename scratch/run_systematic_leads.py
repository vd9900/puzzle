#!/usr/bin/env python3
"""Execute systematic leads against SMALL_B64, INNER_B64, and COSMIC_B64."""
import sys, os, itertools, hashlib
sys.path.insert(0, '/home/vin/bitcoin_puzzle')
sys.path.insert(0, '/home/vin/bitcoin_puzzle/scratch')
from common import DBBI
from systematic_solver import run_sweep, forms_of, check_password

# ==============================================================================
# LEAD 1: Dutch Contextual, Personal, and Movie Slang
# ==============================================================================
dutch_cands = [
    # Two doors & choice
    'twee deuren', 'tweedeuren', 'de twee deuren', 'tweede deur', 'tweededeur',
    'deur naar rechts', 'deurnaarrechts', 'rechterdeur', 'de rechterdeur',
    'deur naar links', 'deurnaarlinks', 'linkerdeur', 'de linkerdeur',
    'de andere deur', 'andere deur', 'anderedeur', 'er is nog een deur', 'er is een andere deur',
    'redding van zion', 'reddingvanzion', 'de bron en de redding van zion', 'de bron', 'debron',
    'terug naar de matrix', 'terugnaardematrix', 'naar haar', 'naarhaar',
    'het probleem is keuze', 'hetprobleemiskeuze', 'keuze', 'keuzes', 'de keuze', 'dekeuze',
    'het probleem is de keuze',
    'zij gaat dood en er is niets dat je kunt doen om het te stoppen',
    'zij gaat dood en er is niets dat je kan doen om het te stoppen',
    'er is niets dat je kunt doen om het te stoppen',
    'er is niets dat je kan doen om het te stoppen',
    'niets dat je kunt doen om het te stoppen',
    'niets dat je kan doen om het te stoppen',
    'als ik jou was zou ik hopen dat we elkaar niet meer ontmoeten',
    'als ik jou was zou ik hopen dat we elkaar niet meer zien',
    'dat doen we niet', 'datdoenweniet', 'dat zullen we niet', 'datzullenweniet',
    'we zien elkaar niet meer', 'wezienelkaarnietmeer', 'we zullen niet', 'wezullenniet',
    'hoop het is de ultieme menselijke waan', 'de ultieme menselijke waan',
    'hoop het is de typische menselijke waan', 'menselijke waan',

    # Half and better half
    'helft en betere helft', 'helftenbeterehelft', 'betere helft', 'beterehelft',
    'de betere helft', 'debeterehelft', 'mijn betere helft', 'mijnbeterehelft',
    'wederhelft', 'mijn wederhelft', 'de wederhelft', 'wederhelften',
    'de helft en de betere helft', 'dehelftendebeterehelft',
    'ze hebben ook fondsen nodig om te leven', 'ze hebben ook geld nodig om te leven',
    'en ze hebben ook fondsen nodig om te leven', 'fondsen om te leven',

    # Last words before archi choice
    'laatste woorden voor archi keuze', 'laatstewoordenvoorarchikeuze',
    'laatste woorden voor de archi keuze', 'laatstewoordenvoordearchikeuze',
    'laatste woorden voor archis keuze', 'laatstewoordenvoorarchiskeuze',
    'laatste woorden voor de keuze', 'laatstewoordenvoordekeuze',
    'woorden voor de keuze', 'woordenvoordekeuze',
    'voor de keuze', 'voordekeuze', 'voor archi keuze', 'voorarchikeuze',
    'dit wachtwoord', 'ditwachtwoord',

    # Close friends & South Park
    'kwaliteitsvrienden', 'kwaliteit vrienden', 'kwaliteitvrienden',
    'goede vrienden', 'goedevrienden', 'mijn goede vrienden', 'mijngoedevrienden',
    'beste vrienden', 'bestevrienden', 'hechte vrienden', 'hechtevrienden',
    'mijn hechte vrienden', 'mijnhechtevrienden',
    'vrienden en familie', 'vriendenenfamilie',
    'als je kwaliteitsvrienden wilt vinden moet je eerst door alle lullen waden',
    'als je goede vrienden wilt vinden moet je eerst door alle lullen waden',
    'door alle lullen waden', 'waden door alle lullen',
    'je hebt 0 vrienden', 'je hebt nul vrienden', 'jehebt0vrienden', 'jehebtnulvrienden',
    'nul vrienden', 'nulfriends', '0 vrienden', '0vrienden',

    # Creator expressions & inside jokes
    'geestverruimend', 'geest verruimend', 'tasteless alcohol', 'smaakloze alcohol',
    'hersencellen doden', 'doodt hersencellen', 'it kills braincells', 'it kills brain cells',
    'paarse wortels', 'paarsewortels', 'oranje wortels', 'oranjewortels',
    'de wortels waren paars', 'wortels waren paars',
    'tijd om gras aan te raken', 'gras aanraken', 'touch grass', 'touchgrass',
    'super covid-20', 'supercovid20', 'covid-20', 'covid20',
    '24h killswitch', '24hkillswitch', 'killswitch',
    'dozers spul', 'dozers stuff', 'dozer spul', 'dozer stuff',
    'blije halvering', 'fijne halvering', 'happy halving', 'happyhalving',
    'halvering', 'halving',
    'tot over 4 jaar', 'totover4jaar', 'see you in 4 years', 'seeyouin4years',
    'alleen btc', 'alleen bitcoin', 'btc only', 'btconly',
    'niet gokken', 'dont gamble', 'dontgamble'
]

# ==============================================================================
# LEAD 2: Exact Architect Speech & Fan Transcript Variants (jaced.com / onebee)
# ==============================================================================
architect_cands = [
    # Exact quotes from jaced.com
    "she is going to die, and there is nothing that you can do to stop it.",
    "she is going to die and there is nothing that you can do to stop it",
    "she is going to die and there is nothing you can do to stop it",
    "she is going to die, and there is nothing you can do to stop it",
    "there is nothing that you can do to stop it",
    "there is nothing you can do to stop it",
    "nothing that you can do to stop it",
    "nothing you can do to stop it",
    "you can do to stop it",
    "can do to stop it",
    "to stop it",
    "stop it",
    "the simple and obvious truth: she is going to die, and there is nothing that you can do to stop it",
    "the simple, and obvious truth: she is going to die, and there is nothing that you can do to stop it",
    "an emotion that is already blinding you from the simple and obvious truth",
    "an emotion that is already blinding you from the simple, and obvious truth",
    "as you adequately put, the problem is choice",
    "as you adequately put the problem is choice",
    "the problem is choice",
    "the problem is",
    "choice. the problem is choice.",
    "choice the problem is choice",
    "there are two doors",
    "two doors",
    "the door to your right leads to the source, and the salvation of zion",
    "the door to your right leads to the source and the salvation of zion",
    "the door to the left leads back to the matrix, to her, and to the end of your species",
    "the door to the left leads back to the matrix to her and to the end of your species",
    "the door to your left leads back to the matrix, to her, and to the end of your species",
    "the door to your left leads back to the matrix to her and to the end of your species",
    "the door to your right",
    "the door to the left",
    "the door to your left",
    "the source, and the salvation of zion",
    "the source and the salvation of zion",
    "the salvation of zion",
    "salvation of zion",
    "salvation",
    "to her, and to the end of your species",
    "to her and to the end of your species",
    "to the end of your species",
    "end of your species",
    "we won't.",
    "we won't",
    "we wont.",
    "we wont",
    "wewont",
    "if i were you, i would hope that we don't meet again.",
    "if i were you i would hope that we don't meet again",
    "if i were you, i would hope that we dont meet again",
    "if i were you i would hope that we dont meet again",
    "i would hope that we don't meet again",
    "i would hope that we dont meet again",
    "hope that we don't meet again",
    "hope that we dont meet again",
    "humph. hope, it is the quintessential human delusion, simultaneously the source of your greatest strength, and your greatest weakness.",
    "humph hope it is the quintessential human delusion simultaneously the source of your greatest strength and your greatest weakness",
    "hope, it is the quintessential human delusion, simultaneously the source of your greatest strength, and your greatest weakness",
    "hope it is the quintessential human delusion simultaneously the source of your greatest strength and your greatest weakness",
    "hope, it is the quintessential human delusion",
    "hope it is the quintessential human delusion",
    "the quintessential human delusion",
    "the source of your greatest strength, and your greatest weakness",
    "the source of your greatest strength and your greatest weakness",
    "apropos, she entered the matrix to save your life at the cost of her own.",
    "apropos she entered the matrix to save your life at the cost of her own",
    "she entered the matrix to save your life at the cost of her own",
    "vis-a-vis, love.",
    "vis-a-vis love",
    "vis a vis love",
    "vis-a-vis",
    "vis a vis",
    "trinity.",
    "trinity",
    "the oracle.",
    "the oracle",
    "which brings us at last to the moment of truth, wherein the fundamental flaw is ultimately expressed, and the anomaly revealed as both beginning, and end.",
    "which brings us at last to the moment of truth, wherein the fundamental flaw is ultimately expressed, and the anomaly revealed as both beginning and end",
    "the moment of truth",
    "the fundamental flaw",
    "both beginning, and end",
    "both beginning and end",
    "beginning and end"
]

# ==============================================================================
# LEAD 3: FAED 32-letter Tail & Segment Representations
# ==============================================================================
tail32 = 'bccahhbiibibbibdcbahaidhfahiihic'
tail32_rev = tail32[::-1]
d1 = tail32.translate(str.maketrans('abcdefghi', '123456789'))
d0 = tail32.translate(str.maketrans('abcdefghi', '012345678'))
d1_rev = d1[::-1]
d0_rev = d0[::-1]

faed_tail_cands = [
    tail32,
    tail32_rev,
    ' '.join(tail32),
    d1,
    d0,
    d1_rev,
    d0_rev,
    ' '.join(d1),
    ' '.join(d0),
]

# Try hex interpretations if valid
try:
    faed_tail_cands.append(bytes.fromhex(d1).decode('latin-1'))
    faed_tail_cands.append(bytes.fromhex(d0).decode('latin-1'))
except: pass

# ==============================================================================
# LEAD 4: R60 / R61 and Clean Token Representations
# ==============================================================================
r60 = 'difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'
r61 = r60 + 'e'
r56 = ''.join(c for c in DBBI.replace('be', '') if c != 'b')

r_cands = [
    r60, r60[::-1],
    r61, r61[::-1],
    r56, r56[::-1],
    r60.translate(str.maketrans('abcdefghi', '123456789')),
    r60.translate(str.maketrans('abcdefghi', '012345678')),
    r61.translate(str.maketrans('abcdefghi', '123456789')),
    r61.translate(str.maketrans('abcdefghi', '012345678')),
]

# ==============================================================================
# LEAD 5: GSMG Farewell & Team Personal Slang
# ==============================================================================
team_cands = [
    'JRK', 'jrk', 'd0d', 'Darky', 'darky', 'Bloctite', 'bloctite', 'Ewout', 'ewout', 'EwoutM', 'ewoutm',
    'SoWut', 'sowut', 'SoWut?', 'Jrk Bgrt', 'jrk bgrt', 'jrk_bgrt', 'jrkbgrt',
    'JRK, d0d, Darky, Bloctite', 'JRK, d0d, Darky, Bloctite, and the remaining GSMG crew',
    'JRK d0d Darky Bloctite', 'jrk d0d darky bloctite', 'jrkd0ddarkybloctite',
    'With love, zero regrets', 'with love, zero regrets', 'with love zero regrets', 'withlovezeroregrets',
    'zero regrets', 'zeroregrets',
    'Stay dangerous out there, stack sats and may your future entries always be better than your exits',
    'stay dangerous out there, stack sats and may your future entries always be better than your exits',
    'Stay dangerous out there', 'stay dangerous out there', 'stay dangerous', 'staydangerous',
    'stack sats', 'stacksats',
    'may your future entries always be better than your exits', 'better than your exits',
    'The lights are going off, but the story? That one lives forever',
    'The lights are going off but the story that one lives forever',
    'That one lives forever', 'that one lives forever', 'thatonelivesforever',
    'Thank you for trusting a bunch of idiots with a dream', 'a bunch of idiots with a dream',
    'abunchofidiotswithadream',
    'Nine years of chaos ended', 'One mystery remains', 'nine years of chaos ended one mystery remains',
    'Nine years of chaos ended. One mystery remains.',
    'Follow the white rabbit', 'follow the white rabbit', 'followthewhiterabbit',
    'WARNING: carrier anomaly', 'carrier anomaly', 'carrieranomaly'
]

# Run all sweeps systematically
if __name__ == '__main__':
    print('Starting systematic sweeps over concrete leads...\n')
    run_sweep(dutch_cands, 'LEAD 1: Dutch Contextual/Slang')
    run_sweep(architect_cands, 'LEAD 2: Architect Scene Quotes')
    run_sweep(faed_tail_cands, 'LEAD 3: FAED Tail & Segments')
    run_sweep(r_cands, 'LEAD 4: Residual R60/R61')
    run_sweep(team_cands, 'LEAD 5: GSMG Farewell & Team')
    print('\nAll systematic sweeps complete.')
