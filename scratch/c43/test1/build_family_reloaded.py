"""Build the 'speech family' Reloaded text: the Zion Mainframe 2003 full-film transcript with its Architect scene
(lines 755-786, 'Architect: Hello, Neo.' .. 'Architect: We won't.') replaced by the jaced.com 2003-05-15 scene
transcript (the family the Phase 3.2 speech was copied from: 'to sedulously avoid it').
Usage: python3 -I build_family_reloaded.py JACED_HTML TMRL_TXT OUT_SCENE OUT_SPLICED"""
import sys, re, html
jh, tm, out_scene, out_spliced = sys.argv[1:5]
t = open(jh, encoding='utf-8', errors='replace').read()
t = re.sub(r'(?s)<script.*?</script>|<style.*?</style>', '', t)
t = html.unescape(re.sub(r'<[^>]+>', '\n', t))
lines = [l.strip() for l in t.splitlines() if l.strip()]
a = next(k for k, l in enumerate(lines) if 'Hello, Neo' in l)
b = next(k for k, l in enumerate(lines) if k > a and l.startswith('The Architect - We won'))
scene = []
for l in lines[a:b + 1]:
    if l.startswith('*'):          # stage direction
        continue
    m = re.match(r"^((?:The )?Architect|Neo)\s+-\s+(.*)$", l)
    scene.append(f'{m.group(1)}: {m.group(2)}' if m else l)  # continuation lines kept as text
open(out_scene, 'w').write('\n'.join(scene) + '\n')
tl = open(tm, encoding='utf-8', errors='replace').read().splitlines()
assert tl[754].startswith('Architect: Hello, Neo.') and tl[785].startswith("Architect: We won't."), (tl[754], tl[785])
open(out_spliced, 'w').write('\n'.join(tl[:754] + scene + tl[786:]) + '\n')
print('scene lines', len(scene), 'spliced lines', len(tl[:754] + scene + tl[786:]))
