import urllib.request,re,html,pathlib
out=pathlib.Path('D:/Xaramada-Modwork/armadafiles-bajor')
for name,path in [('ships','ships/bajoran-ship-pack-v10'),('station','stations/other/bajoran-starbase-20')]:
 u='http://armadafiles.com/files/armada-2/'+path+'/summary/download'
 with urllib.request.urlopen(u,timeout=20)as r:b=r.read();print(name,r.headers.get('Content-Type'),len(b),r.url)
 (out/(name+'-download-response')).write_bytes(b)
 if b[:2]==b'PK':print('ZIP',name)
 else:
  s=b.decode(errors='replace');print('\n'.join(html.unescape(x)for x in re.findall(r'(?:href|action)=["\x27]([^"\x27]+)',s)if any(k in x for k in ['download','zip','task'])))
