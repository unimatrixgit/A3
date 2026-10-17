import urllib.request,urllib.parse,re,html,pathlib,json,concurrent.futures,time
root='http://armadafiles.com';out=pathlib.Path('D:/Xaramada-Modwork/armadafiles-bajor');pending={root+'/files/armada-2/ships',root+'/files/armada-2/stations'};seen=set();details=set();matches=[];failed=[]
def fetch(u):
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=15)as r:return u,r.read().decode('utf-8',errors='replace')
 except Exception as e:return u,None
while pending:
 batch=sorted(pending-seen)[:12]
 if not batch:break
 pending.difference_update(batch);seen.update(batch)
 with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:
  for u,s in pool.map(fetch,batch):
   if s is None:failed.append(u);continue
   (out/('listing-'+str(len(seen))+'-'+str(batch.index(u))+'.html')).write_text(s)
   for x in re.findall(r'href=["\x27]([^"\x27]+)',s):
    v=urllib.parse.urljoin(u,html.unescape(x)).split('#')[0]
    if not any(v.startswith(root+'/files/armada-2/'+sect)for sect in ['ships','stations']):continue
    if v.endswith('/details'):details.add(v)
    elif not any(z in v for z in ['summary','download','?']):
     if v not in seen:pending.add(v)
   for chunk in re.split(r'<h3\b',s):
    if re.search('bajor',chunk,re.I):
     links=[urllib.parse.urljoin(u,html.unescape(x))for x in re.findall(r'href=["\x27]([^"\x27]+)',chunk)if '/details'in x]
     if links:matches.append({'listing':u,'links':links,'text':re.sub('<[^>]+>',' ',chunk)[:2000]})
 print('Listings scanned',len(seen),'detail entries',len(details),'pending',len(pending),flush=True)
 if len(seen)>400:break
report={'listingPages':len(seen),'detailEntries':len(details),'details':sorted(details),'listingMatches':matches,'failedListings':failed,'pending':sorted(pending)};(out/'catalogue-scan.json').write_text(json.dumps(report,indent=2));print('MATCHES',json.dumps(matches),flush=True)
