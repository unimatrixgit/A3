import urllib.request,re,html,json,pathlib,concurrent.futures,urllib.parse
out=pathlib.Path('D:/Xaramada-Modwork/armadafiles-bajor');out.mkdir(exist_ok=True)
def fetch(url):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20)as r:return r.read().decode('utf-8',errors='replace')
 except Exception as e:return None
u='http://armadafiles.com/files/armada-2/ships/bajoran-ship-pack-v10/details';s=fetch(u);(out/'ship-pack.html').write_text(s or'')
for x in re.findall(r'href=["\x27]([^"\x27]+)',s or''):
 if any(a in x for a in ['download','summary']):print(html.unescape(x))
for section in ['ships','stations']:
 url='http://armadafiles.com/files/armada-2/'+section;s=fetch(url);(out/(section+'.html')).write_text(s or'');links=[urllib.parse.urljoin(url,html.unescape(x))for x in re.findall(r'href=["\x27]([^"\x27]+)',s or'')];print(section,'links',list(dict.fromkeys(x for x in links if '/'+section in x))[:40])
