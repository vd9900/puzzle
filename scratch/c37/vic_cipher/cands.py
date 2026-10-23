# Principled VIC key-material candidates (lens vic_cipher, cycle 37).
# Every phrase is a puzzle/song/speech line with an explicit provenance tag; VIC uses its first 20 letters.
import re

# (tag, text). Only lines with >= 20 letters (VIC Line-D needs 20 letters).
PHRASES = [
    # Logic "The Warning" (Phase 1 song) - lines as given in the maintained phase-1 notebook; song start variants
    ('song_start', 'Phase one the seed is planted when opposites attract'),
    ('song_seed', 'The seed is planted when opposites attract'),
    ('song_dig', 'Can you dig it? It takes the physical to create the physical'),
    ('song_phys', 'It takes the physical to create the physical'),
    ('song_p2', 'Phase two the flower blossoms through what seems to be a concrete surface'),
    ('song_flower', 'The flower blossoms through what seems to be a concrete surface'),   # Phase-1 password
    ('song_greed', 'I.e. greed, racism, insanity, physical and social handicaps'),
    ('song_mob', 'These are the things that mob the flower'),
    ('song_rose', 'Red rose or black rose; no in-between'),
    ('song_p3', 'Phase three the judgement if it were to fall upon you today'),
    ('song_judg', 'The judgement if it were to fall upon you today which flower would you be'),
    ('song_iff', 'If it were to fall upon you today, which flower would you be?'),
    ('song_redblack', 'The red rose or the black? This is the warning'),
    ('song_title', 'The warning phase one the seed is planted'),
    # Puzzle strings / stage answers
    ('followrabbit', 'follow the white rabbit'),                       # exactly 20 letters; Phase-0 image alt text
    ('wakeupneo', 'Wake up Neo the matrix has you'),
    ('wakeupyou', 'Wake up you the matrix has you'),
    ('whyamihere', 'Why am I here? Wake up, you... the matrix has you'),
    ('seedplanted', 'gsmg.io/theseedisplanted'),
    ('choice', 'choice is an illusion created between those with power and those without'),
    ('dessert', 'a very special dessert I wrote it myself'),
    ('phase32pw', 'jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple'),
    ('phase3pre', 'causality Safenet Luna HSM'),
    ('genesis', 'The Times 03/Jan/2009 Chancellor on brink of second bailout for banks'),
    ('vicmsg', 'in case you manage to crack this the private keys belong to half and better half'),
    ('lastwords', 'lastwordsbeforearchichoice'),
    ('lastwordspw', 'lastwordsbeforearchichoicethispassword'),
    ('shabef', 'shabef our first hint is your last command'),
    ('firsthint', 'our first hint is your last command'),
    ('gsmgslogan', 'GSMGIO5BTCPUZZLECHALLENGE'),
    ('magicpiece', 'gsmg.io magic puzzle piece'),
    ('whiterabbits', 'White Rabbits everywhere'),
    ('roses', 'Roses are White but often Red'),
    ('yellow', 'Yellow has a number and so does Blue'),
    ('goback', 'Go back to the first puzzle piece without further ado'),
    ('onedoor', 'It might have shown you only one door'),
    ('rabbitsnest', 'beware that the rabbits nest may contain a whole lot more'),
    ('anotherdoor', 'There is another door'),          # 18 letters -> padded by following words below
    ('anotherdoor2', 'There is another door might be found'),
    # Phase 3.2 Architect speech + chess clue
    ('arch_wait', "I've been waiting for you"),        # exactly 20 letters
    ('arch_questions', 'You have many questions'),         # exactly 20 letters
    ('arch_conscious', 'although the process has altered your consciousness'),
    ('arch_designed', "I've designed you a beautiful strategic position"),
    ('arch_onefor', 'One for one, four for one.'),          # 19 letters -> skipped by phrase20 unless extended
    ('raising', 'Raising the stakes without extra chances of winning'),
    ('fubcd', 'A fubcd-king & oracle-queen, thingky mvps, on a sad board'),
    ('sadboard', 'on a sad board but as wide as the first one seen'),
    # Beaufort speech sentences (research/artifacts/phase32-beaufort.txt)
    ('b_life', 'your life is the sum of a remainder of an unbalanced equation'),
    ('b_anomaly', 'you are the eventuality of an anomaly'),
    ('b_find', 'please if you find a way to complete the last part of the puzzle'),
    ('b_wiseman', 'what a wise man above hinted at is worth hundred fourty'),
    ('b_source', 'the function of the you is now to return to the source codes'),
    ('b_prime', 'reinserting the prime basics'),
    ('b_select', 'after which you will be required to select from over twenty three ciphers'),
    ('b_brute', 'note that also brute forcing might be required'),
    ('b_goodluck', 'good luck nevertheless i really hope youre the one'),
    ('b_theone', 'i really hope youre the one ciao bella o'),
    ('b_denial', 'denial is the most predictable of all human responses'),
]

def letters(s):
    return re.sub('[^A-Za-z]', '', s).upper()

def usable_phrases():
    out = []
    seen = set()
    for tag, p in PHRASES:
        L = letters(p)
        if len(L) < 20:
            continue
        if L[:20] in seen:
            continue
        seen.add(L[:20])
        out.append((tag, L[:20]))
    return out

# Dates: VIC uses the date written numerically, no leading zeros, first 6 digits (5 for Line-B, 6th = keygroup position).
DATES = [
    ('neo_DMY', '1192001'),      # 11/9/2001  (Hayhanen style, 3 Sep 1945 -> 391945)
    ('neo_MDY', '9112001'),      # 9/11/2001
    ('neo_DDMMYYYY', '11092001'),
    ('neo_MMDDYYYY', '09112001'),
    ('neo_DDMMYY', '110901'),     # 11 SEP 01 passport style
    ('neo_MMDDYY', '091101'),
    ('neo_YYYYMMDD', '20010911'),
    ('neo_YMD', '2001911'),
    ('neo_YYMMDD', '010911'),
    ('launch_DMY', '1342019'),
    ('launch_MDY', '4132019'),
    ('launch_DDMMYYYY', '13042019'),
    ('launch_YYYYMMDD', '20190413'),
    ('genesis_DMY', '312009'),
]

PNUMS = list(range(1, 21))  # wa+wb must fit in the 50-digit block

if __name__ == '__main__':
    ps = usable_phrases()
    print(len(ps), 'phrases'); [print(t, p) for t, p in ps]
    print(len(DATES), 'dates', len(PNUMS), 'pnums')
