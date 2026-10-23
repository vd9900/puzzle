import sys, time; sys.argv=['x']; sys.path.insert(0,'.')
import run_main as R, vicfast as V, vic, beam, numpy as np
T=R.make_targets()
p=T['plant1']; a=V.to_idx(p[:565])
k=vic.derive('IVEBEENWAITINGFORYOU','9112001',13,'50731')
u=a[V.untranspose_index(565,k['Q'],k['R'])]
tab=V.board_tables(k['S'])
for X in [None, 6, 3]:
    t=time.time(); sc,txt=beam.beam_decode(u,'a1',tab,X=X); print('X',X,'score %.3f'%sc, 'qscore %.3f'%V.qscore(txt), '%.1fs'%(time.time()-t), txt[:90])
txt0=R.corpus()[20000:20420].lower(); print('truth', txt0[:90])
# control: wrong key
k2=vic.derive('IVEBEENWAITINGFORYOU','9112001',12,'50731')
u2=a[V.untranspose_index(565,k2['Q'],k2['R'])]
for X in [None,6]:
    sc,txt=beam.beam_decode(u2,'a1',V.board_tables(k2['S']),X=X); print('wrong X',X,'%.3f'%sc,'q %.3f'%V.qscore(txt), txt[:80])
