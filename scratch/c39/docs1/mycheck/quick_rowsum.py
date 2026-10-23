# Own re-implementation (not the community code) of two trivial deterministic readings seen in the docs.
A="dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe"
B=open('/home/vin/bitcoin_puzzle/scratch/c39/docs1/mycheck/faed.txt').read().strip()
assert len(A)==91 and len(B)==570
V={c:i+1 for i,c in enumerate("abcdefghi")}
G="00110b0010110y 11b1001110b011 1101110b001001 0110b000011101 0b1000110y0110 100110y010y011 100b1100010y00 b11000000010y0 00011b0111110b 11b111y0110001 1101000y011011 11110010b01100 0b0111010y0110 01b0110110b011".split()
def isp(n): return n>1 and all(n%d for d in range(2,int(n**.5)+1))
# (1) dbbi as upper triangle of symmetric 14x14 (91=C(14,2)), row sums K; faed rows of 15 -> R (38); chr((R^K)%26+65)
def key(z=set()):
    M=[[0]*14 for _ in range(14)];k=0
    for i in range(14):
        for j in range(i+1,14):
            M[i][j]=M[j][i]=0 if (i+1,j+1) in z else V[A[k]]; k+=1
    return [sum(r) for r in M]
R=[sum(V[c] for c in B[j:j+15]) for j in range(0,570,15)]
ypos={tuple(sorted((r+1,c+1))) for r,row in enumerate(G) for c,x in enumerate(row) if x=='y'}
for name,K in (("S",key()),("H",key(ypos))):
    print(name, ''.join(chr(((R[i]^K[i%14])%26)+65) for i in range(38)), "K=",K)
# (2) faed 30x19 row sums, prime sums -> chr
rs=[sum(V[c] for c in B[r*19:(r+1)*19]) for r in range(30)]
print("rowsums19", rs, "primes->", ''.join(chr(s) for s in rs if isp(s)))
# (3) "L" variant: zero faed cells whose (row,col,letter) hits blue-row/yellow-col/prime-blue-letter sets
pos=lambda ch:[(r*14+c+1) for r,row in enumerate(G) for c,x in enumerate(row) if x==ch]
blue=pos('b'); yellow=pos('y')
mod=lambda xs,m:{(x-1)%m+1 for x in xs}
letters={"abcdefghi"[i-1] for i in mod([p for p in blue if isp(p)],9)}
rb=mod(blue,38); cy=mod(yellow,15)
RL=[sum(0 if ((i//15+1) in rb and (i%15+1) in cy and B[i] in letters) else V[B[i]] for i in range(j,j+15)) for j in range(0,570,15)]
K=key()
print("L", ''.join(chr(((RL[i]^K[i%14])%26)+65) for i in range(38)))
