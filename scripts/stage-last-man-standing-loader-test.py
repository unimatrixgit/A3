from pathlib import Path
import struct,re,uuid,json,shutil,hashlib
r=Path('D:/armadaIII');repo=Path('D:/aramada');stage=Path('D:/Xaramada-Modwork/last-man-standing/loader-test');stage.mkdir(exist_ok=True);source=r/'bzn/a2_fed01.bzn';b=source.read_bytes();title='Last Man Standing Loader Test';name='LastManStandingTest.bzn'
# Replace only verified typed-string records,adjusting both serialized lengths.
changes=[]
for i in range(len(b)-20):
 if b[i:i+8]!=struct.pack('<II',4,4):continue
 n,res,n2=struct.unpack_from('<III',b,i+8)
 if n!=n2 or res!=0 or n>256:continue
 val=b[i+20:i+20+n]
 mapping={b'MISSION_FED_1_MAIN_TITLE':title.encode(),b'a2_fed01.bzn':name.encode(),b'a2_fed01.tt':b'tech1.tt',b'a2_fed01R.drl':b''}
 if val in mapping:
  new=mapping[val];changes.append((i,i+20+n,struct.pack('<IIIII',4,4,len(new),0,len(new))+new))
for start,end,new in reversed(changes):b=b[:start]+new+b[end:]
# EmptyMission stores fixed64-byte script,rules andtitle fields.
o=b.index(b'EmptyMission');assert b.count(b'EmptyMission')==1
first=b.find(struct.pack('<II',2,64),o,o+100);assert first!=-1
for field,val in [(first,b'mmm_loader.dll'),(first+72,b''),(first+144,title.encode())]:
 assert struct.unpack_from('<I',b,field+4)[0]==64
 b=b[:field+8]+val+b'\0'*(64-len(val))+b[field+72:]
assert b'a2_fed01R.drl'not in b and b'a2_fed01S.dsl'not in b
p=stage/'bzn'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
base=Path('D:/Xaramada-Modwork/last-man-standing/research/mmm-extracted/mmm');dst=stage/'missions/mmm_loader.dll';dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(base/'missions/mmm_loader.dll',dst)
# Add diagnostic mission to existing tutorial/misc selection,preserving campaign entries.
p=r/'mshell.set';text=p.read_text(encoding='latin1');lines=text.splitlines();i=next(i for i,x in enumerate(lines)if x.strip()=='-');lines.insert(i,name);(stage/'mshell.set').write_text('\n'.join(lines)+'\n',encoding='latin1')
label=(r/'label.map').read_text(encoding='latin1');m=re.search(r'\bmission_select\s*\{',label);assert m;label=label[:m.end()]+f'\n    + {name} {{Last Man Standing - Loader Test}}\n'+label[m.end():];(stage/'label.map').write_text(label,encoding='latin1')
report=dict(stage=str(stage),source=str(source),sourceHash=hashlib.sha256(source.read_bytes()).hexdigest(),map=name,typedStringChanges=len(changes),installed=False,gameplayVerified=False,notes=['Native original mission terrain/objects retained for compatibility smoke test.','Original campaign DSL/DRL links removed in copiedmap only.','Adds one miscellaneous/tutorial mission entry;preserves original campaign lists.','Diagnostic loader test only;not complete Last Man Standing mode.']);(repo/'reports/last-man-standing-loader-test.json').write_text(json.dumps(report,indent=2));print('Staged native-map loader smoke test;original campaign untouched.')
