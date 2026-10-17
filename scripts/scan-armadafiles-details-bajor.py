import pathlib,json,urllib.request,concurrent.futures,re,time
out=pathlib.Path('D:/Xaramada-Modwork/armadafiles-bajor');r=json.loads((out/'catalogue-scan.json').read_text());matches=[];failed=[]
def fetch(u):
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=12)as f:s=f.read().decode('utf-8',errors='replace')
  # Match article text, excluding navigation/sidebar comments where possible.
  title=re.search(r'<title>(.*?)</title>',s,re.S);text=re.sub('<[^>]+>',' ',s);hits=[text[max(0,m.start()-180):m.end()+420]for m in re.finditer('bajor',text,re.I)]
  return {'url':u,'title':title[1]if title else'', 'mentions':hits,'html':s if hits else None}
 except Exception as e:return {'url':u,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:
 for i,x in enumerate(pool.map(fetch,r['details']),1):
  if 'error'in x:failed.append(x)
  elif x['mentions']:
   html=x.pop('html');(out/('match-'+str(len(matches))+'.html')).write_text(html);matches.append(x)
  if i%100==0:print('Detail pages',i,'/',len(r['details']),'Bajor mentions',len(matches),'failed',len(failed),flush=True)
(out/'detail-scan.json').write_text(json.dumps({'pages':len(r['details']),'matches':matches,'failed':failed},indent=2));print('RESULT',json.dumps(matches),flush=True)
