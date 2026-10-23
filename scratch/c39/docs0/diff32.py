import sys, base64, hashlib, difflib
sys.path.insert(0,'/home/vin/bitcoin_puzzle/scratch')
from common import evp
from Crypto.Cipher import AES
def dec(path,pw):
    b=base64.b64decode(''.join(open(path).read().split()))
    k,iv=evp(hashlib.sha256(pw.encode()).hexdigest().encode(),b[8:16],'sha256')
    pt=AES.new(k,AES.MODE_CBC,iv).decrypt(b[16:]); return pt[:-pt[-1]], b[8:16].hex()
old,s1=dec('/home/vin/Downloads/Telegram Desktop/ChatExport_2026-10-13/files/phase3.1_old.aes','jacquefrescogivetitjustonesecondheisenbergsuncertaintyprinciple')
new,s2=dec('/home/vin/bitcoin_puzzle/data/user_supplied/telegram/docs/export_files/Gsmg_Salt_Checker.zip__ph.txt','jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple')
print('old',len(old),s1,'new',len(new),s2,'identical',old==new)
sm=difflib.SequenceMatcher(None,old,new,autojunk=False)
for op,a1,a2,b1,b2 in sm.get_opcodes():
    if op!='equal': print(op,a1,a2,b1,b2,'OLD',old[max(0,a1-40):a2+40],'NEW',new[max(0,b1-40):b2+40])
open('old32_plain.bin','wb').write(old); open('new32_plain.bin','wb').write(new)
