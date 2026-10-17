from pathlib import Path
import re,json
root=Path('D:/armadaIII');idx={p.name.lower():p for p in (root/'odf').rglob('*.odf')};errors=[];checked=[]
def props(p,seen=None):
 seen=set()if seen is None else seen
 if p.name.lower()in seen:return {}
 seen.add(p.name.lower());s=p.read_text(encoding='latin1');d={}
 for inc in re.findall(r'(?mi)^[ \t]*#include[ \t]+"([^"\r\n]+)"',s):
  if inc.lower()not in idx:errors.append({'file':p.name,'missingInclude':inc})
  else:d.update(props(idx[inc.lower()],set(seen)))
 for k,v in re.findall(r'(?mi)^[ \t]*(\w+)[ \t]*=[ \t]*([^\r\n]*)',s):d[k.lower()]=v.split('//')[0].strip().strip('"')
 return d
for p in list((root/'odf/ships').glob('bj*.odf'))+[idx['xbjuconst.odf']]+list((root/'odf/stations').glob('bj*.odf')):
 for key,name in props(p).items():
  if not re.fullmatch('weapon[0-9]+',key)or not name:continue
  weapon=idx.get(name.lower()+'.odf')
  if not weapon:errors.append({'unit':p.stem,'missingWeapon':name});continue
  d=props(weapon);label=d.get('classlabel');ordname=d.get('ordname')
  if not label:errors.append({'unit':p.stem,'weapon':name,'missingClassLabel':True})
  if ordname and ordname.lower()+'.odf'not in idx:errors.append({'unit':p.stem,'weapon':name,'missingOrdnance':ordname})
  checked.append({'unit':p.stem,'slot':key,'weapon':name,'classLabel':label,'ordnance':ordname})
out={'target':str(root),'weaponSlotsChecked':len(checked),'errors':errors,'slots':checked,'engineLoadVerified':False,'note':'File resolution only. Existing files and class labels do not prove engine loading succeeds.'}
Path('D:/aramada/reports/bajoran-live-weapon-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'slots':len(checked),'errors':errors}))
