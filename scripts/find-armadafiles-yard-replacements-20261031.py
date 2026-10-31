import urllib.request,re,html,json,concurrent.futures
from pathlib import Path
out=Path('D:/Xaramada-Modwork/armadafiles-yard-replacements');out.mkdir(exist_ok=True)
root='http://armadafiles.com';pending={root+'/files/armada-2/stations/'+n for n in ['federation','borg','klingon','romulan','cardassian','other','species-8472','multi-race']};seen=set();matches={}
def fetch(u):
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=18)as r:return u,r.read().decode(errors='replace')
 except Exception as e:return u,''
for turn in range(5):
 batch=sorted(pending-seen);pending=set()
 if not batch:break
 with concurrent.futures.ThreadPoolExecutor(max_workers=8)as pool:
  for u,s in pool.map(fetch,batch):
   seen.add(u);(out/('list-'+u.split('/stations/')[1].replace('/','_')+'.html')).write_text(s)
   for link in re.findall(r'href=["\x27]([^"\x27]+)',s):
    link=html.unescape(link);link=root+link if link.startswith('/')else link
    if '/files/armada-2/stations/'not in link:continue
    if link.endswith('/details')and any(x in link.lower()for x in ['yard','dock','stationpack','station-pack','borg-base']):matches[link]=u
    if '/page-'in link and '?'not in link and link not in seen:pending.add(link)
 print('Pages',len(seen),'candidates',len(matches),flush=True)
(out/'catalogue.json').write_text(json.dumps({'pages':sorted(seen),'candidates':matches},indent=2));print('\n'.join(matches))
