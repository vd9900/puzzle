# Own check: MadHatter (ePrint 2020/301) ciphertext = 4-symbol blocks of DISTINCT letters a-i, one per digit group (2,2,2,3).
B=open('/home/vin/bitcoin_puzzle/scratch/c39/docs1/mycheck/faed.txt').read().strip()
A="dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe"
for name,s in (("faed",B),("dbbi",A)):
    for off in range(4):
        blocks=[s[i:i+4] for i in range(off,len(s)-3,4)]
        bad=sum(len(set(b))<4 for b in blocks)
        print(name,"len",len(s),"offset",off,"blocks",len(blocks),"blocks_with_repeat",bad)
