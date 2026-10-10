from wordroot import *
f=letters_to_digits(FAED); d=letters_to_digits(DBBI)
RES60='difhccgihaeeihggegebgehhehhfafdhffcdbfcccgfeggecdcifffgigeea'; r60=letters_to_digits(RES60)
texts={}
texts['speech32']=open('speech32_words.txt').read()
texts['arch_chat']=open('arch_scene_chat.txt').read()
texts['cb322']="IN CASE YOU MANAGE TO CRACK THIS THE PRIVATE KEYS BELONG TO HALF AND BETTER HALF AND THEY ALSO NEED FUNDS TO LIVE"
import pathlib
texts['phase2']=pathlib.Path('/home/vin/bitcoin_puzzle/research/artifacts/phase2.txt').read_text(errors='ignore')
texts['phase3']=pathlib.Path('/home/vin/bitcoin_puzzle/research/artifacts/phase3.txt').read_text(errors='ignore')
texts['phase32head']=pathlib.Path('/home/vin/bitcoin_puzzle/research/artifacts/phase32.txt').read_bytes()[:700].decode('latin-1')
texts['phase2html']=pathlib.Path('/home/vin/bitcoin_puzzle/research/sources/phase2.html').read_text()
texts['readme']=pathlib.Path('/home/vin/bitcoin_puzzle/research/sources/community-README.md').read_text()
targets={'faed':f,'dbbi':d,'res60':r60,'faed_h1':f[:285],'faed_h2':f[285:]}
import random
for tn,text in texts.items():
    ws=words_of(text)
    for mode in ('dr9','dr0','mod10','sum','len','lenmod9'):
        rs=root_string(ws,mode)
        for gn,g in targets.items():
            L,ia,ib=lcs_substring(rs,g)
            m,n,off=best_alignment(rs,g)
            flag=' <<<' if L>=9 or m/n>0.25 else ''
            if L>=8 or m/n>0.22 or mode=='dr9' and gn in('faed','res60'):
                print(f'{tn:12s} {mode:7s} words={len(ws):4d} vs {gn:7s}: LCS={L:2d}@{ia}/{ib}  align={m}/{n} off={off}{flag}')
# null: random digit strings with faed's distribution vs speech roots
