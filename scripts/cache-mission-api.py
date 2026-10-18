from pathlib import Path
import urllib.request,re,concurrent.futures,json,html
out=Path('D:/Xaramada-Modwork/last-man-standing/research/api');out.mkdir(exist_ok=True);seed=Path('D:/Xaramada-Modwork/last-man-standing/research/libraries.html').read_text();urls=set(re.findall(r'href="(http://guide.fleetops.net/guide/[0-9a-f]{13})"',seed));seen=set();data=[]
def get(url):
 try:return url,urllib.request.urlopen(url,timeout=12).read().decode()
 except Exception:return url,''
for depth in range(3):
 jobs=urls-seen;seen.update(jobs)
 for url,s in concurrent.futures.ThreadPoolExecutor(6).map(get,jobs):
  if not s:continue
  title=re.search(r'<title>(.*?)</title>',s,re.S);title=html.unescape(title[1])if title else url;slug=url.rsplit('/',1)[1];(out/(slug+'.html')).write_text(s,encoding='utf-8');data.append(dict(url=url,title=title,file=slug+'.html'));urls.update(re.findall(r'href="(http://guide.fleetops.net/guide/[0-9a-f]{13})"',s))
(out/'index.json').write_text(json.dumps(data,indent=2));print(json.dumps([x for x in data if any(k in x['title']for k in ['Entity','Player','Save','Load','GameObject','Monitor','Timer','Vector','Craft','MMM','App','Resource'])],indent=2));print('Cached',len(data),'reference pages')
