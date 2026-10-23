# public archive.org full-text search (guest, same as the website "Search text contents" box); prints snippets for our two items
import sys, json, urllib.request, urllib.parse, time
IDS={'cosmicdualitymys0000time','cosmicduality00time'}
def q(query, n=20):
    url='https://archive.org/services/search/beta/page_production/?'+urllib.parse.urlencode(dict(user_query=query,service_backend='fts',hits_per_page=n,page_type='collection_details',page_target='inlibrary'))
    import subprocess; d=json.loads(subprocess.run(['curl','-s','-m','60',url],capture_output=True,text=True).stdout)
    b=d['response'].get('body') or {}
    out=[]
    for h in (b.get('hits') or {}).get('hits',[]):
        f=h.get('fields',{})
        if f.get('identifier') in IDS:
            out.append((f.get('identifier'),h.get('highlight',{}).get('text',[])))
    return out
if __name__=='__main__':
    for qq in sys.argv[1:]:
        print('#### QUERY',qq)
        try: res=q(qq)
        except Exception as e:
            print('   ERR',e); time.sleep(4)
            try: res=q(qq)
            except Exception as e2: print('   ERR2',e2); res=[]
        for ident,snips in res:
            print('  ',ident)
            for s in snips: print('     >',s.replace('\n',' / '))
        time.sleep(3)
