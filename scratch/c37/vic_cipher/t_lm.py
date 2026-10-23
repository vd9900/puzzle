import sys; sys.argv=['x']; sys.path.insert(0,'.')
import run_main as R, vicfast as V, vic, numpy as np, random
T=R.make_targets()
p=T['plant1']; body=p[:565]; a=V.to_idx(body)
k=vic.derive('IVEBEENWAITINGFORYOU','9112001',13,'50731')
idx=V.untranspose_index(565,k['Q'],k['R'])
u=a[idx]; ds=V.letters_to_digit_list(u,'a1')
tab=V.board_tables(k['S']); t=V.cb_decode_digits(ds,tab)
print('plant1 right key greedy decode:', t[:100], V.qscore(t))
print('p32 board on same:', V.qscore(V.cb_decode_digits(ds,V.board_tables(kind='p32'))))
# wrong keys
rnd=random.Random(2); sc=[]
for _ in range(300):
    Q=[rnd.randrange(10) for _ in range(rnd.randint(8,28))]; Rr=[rnd.randrange(10) for _ in range(rnd.randint(8,28))]
    S=list(range(10)); rnd.shuffle(S)
    u=a[V.untranspose_index(565,Q,Rr)]; ds=V.letters_to_digit_list(u,'a1')
    sc.append(V.qscore(V.cb_decode_digits(ds,V.board_tables(S))))
sc=np.array(sc); print('wrong keys qscore mean %.3f sd %.3f max %.3f'%(sc.mean(),sc.std(),sc.max()))
# correct transposition but wrong S
sc2=[]
u=a[idx]; ds=V.letters_to_digit_list(u,'a1')
for _ in range(300):
    S=list(range(10)); rnd.shuffle(S); sc2.append(V.qscore(V.cb_decode_digits(ds,V.board_tables(S))))
print('right transposition, random S: mean %.3f max %.3f'%(np.mean(sc2),np.max(sc2)))
import time; t0=time.time()
for _ in range(1000): V.qscore(V.cb_decode_digits(ds,tab))
print('ms per decode+score', (time.time()-t0))
