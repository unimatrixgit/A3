from pathlib import Path
import re,json,urllib.request,urllib.parse,concurrent.futures,html
base='http://armadafiles.com/files/armada-2/maps/8-player';work=Path('D:/Xaramada-Modwork/eight-player-completion');work.mkdir(exist_ok=True)
def fetch(u):
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=20)as r:return r.read()
 except Exception as e:return None
links=set();listings=[]
for n in range(1,9):
 u=base+('/page-'+str(n)if n>1 else'');b=fetch(u)
 if not b:continue
 s=b.decode(errors='replace');listings.append(u)
 for x in re.findall(r'href=["\x27]([^"\x27]+)',s):
  v=urllib.parse.urljoin(u,html.unescape(x))
  if v.startswith(base+'/')and v.endswith('/details'):links.add(v)
print('Catalogued',len(links),'downloads',flush=True)
def inspect(u):
 b=fetch(u)
 if not b:return {'url':u,'error':'Detail fetch failed'}
 s=b.decode(errors='replace');text=html.unescape(re.sub('<[^>]+>',' ',s));title=re.search('<title>(.*?)</title>',s,re.S)[1].split(' - Star Trek')[0];fleet=bool(re.search(r'Fleet\s*(?:Operations|Ops|ops)',text,re.I))
 summary=u.removesuffix('/details')+'/summary/download';data=fetch(summary)
 if not data:return {'url':u,'title':title,'error':'Download fetch failed'}
 name=u.split('/')[-2];p=work/(name+'.archive');p.write_bytes(data)
 return {'url':u,'title':title,'mentionsFleetOps':fleet,'archive':str(p),'bytes':len(data),'downloadUrl':summary}
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
 rows=list(pool.map(inspect,sorted(links)))
(work/'downloads.json').write_text(json.dumps({'listingPages':listings,'downloads':rows},indent=2));print('Downloads saved',sum('archive'in x for x in rows),'failed',sum('error'in x for x in rows),flush=True)
