"""Export the reviewed four-bastion geometry with one hardpoint per weapon bank."""
from pathlib import Path
base=Path('D:/aramada/scripts/stage-vanilla-station-redesign.py').read_text(encoding='utf-8-sig')
base=base.replace("stage=repo/'patches/vanilla-stations-20261026'","stage=repo/'patches/hwp-four-module-20261026'")
base=base.replace("if a['kind']not in ['yard','service','research']:continue","if a['kind']!='hwp':continue")
start=base.index(" if kind in ['yard','service']:\n  exec(yardCode")
end=base.index(' points=np.concatenate',start)
geometry='''
 env=dict(globals());env.update(code=code,unit='tyfghwp'if n=='tybghwp'else n,title=title)
 exec(hwpGeometry,env)
 allparts=env['parts'];central=source=env['source'];mountPositions=env['positions']
'''
base=base[:start]+geometry+base[end:]
insert="""
 # Give each existing bank its own visible emitter; retain all legacy system nodes.
 t=odfs[n].read_text(encoding='latin1');beforeProps=props(n)
 for mount in mountPositions:
  slot=mount['slot'];hp='hwpbank'+str(slot);world=(np.array(mount['position'])-center)/span*size;local=(inv@np.r_[world,1])[:3]
  model.nodes.append({'id':hp,'parent':parent['id'],'type':'NULL_OR_HARDPOINT','local_transform':inv[:3,:3].T.tolist()+[local.tolist()],'data':None})
  t=put(t,'weaponHardpoints'+str(slot),'"'+hp+'"')
  assert beforeProps['weapon'+str(slot)]==loadouts[n]['weapons'][slot-1]['odf'],(n,slot)
 rel=odfs[n].relative_to(root);f=O/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(t.replace('\\r','').replace('\\n','\\r\\n').encode('latin1'))
 afterProps={k.lower():v.split('//')[0].strip().strip('"')for k,v in re.findall(r'(?mi)^[ \\t]*(\\w+)[ \\t]*=[ \\t]*([^\\r\\n]*)',t)}
 diff={k for k in beforeProps.keys()|afterProps.keys()if beforeProps.get(k)!=afterProps.get(k)}
 assert diff=={'weaponhardpoints'+str(i)for i in range(1,17)},(n,diff)
"""
base=base.replace(" path=O/'SOD'/(alias+'.sod');",insert+" path=O/'SOD'/(alias+'.sod');")
base=base.replace("else(85,175,255);dr=", "else(245,85,70);dr=")
base=base.replace("else'yard'),(4,4)","else'defence'),(4,4)")
base=base.replace("'architecture':'approved vanilla-derived 20261026'","'architecture':'four-module HWP fortress 20261026','weaponMounts':mountPositions,'modules':4")
base=base.replace("'odfsChanged':False", "'odfsChanged':'weapon hardpoint names only'")
base=base.replace('Approved vanilla-derived faction yards and research artwork, with Cardassian-derived Bajoran refits. Stats and technology unchanged.','Four-module faction HWP fortresses with sixteen matching weapon mounts and refreshed icons. Existing weapons, costs, size, footprint and functions preserved.')
setup='''
previewScript=(repo/'scripts/preview-hwp-nexus-fortresses.py').read_text(encoding='utf-8-sig');hwpTree=ast.parse(previewScript);hwpLoop=next(x for x in hwpTree.body if isinstance(x,ast.For)and isinstance(x.target,ast.Tuple));hwpBody=[]
for x in hwpLoop.body:
 if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='im'for t in x.targets):break
 hwpBody.append(x)
hwpGeometry=compile(ast.Module(body=hwpBody,type_ignores=[]),'reviewed-hwp-geometry','exec');rows=json.loads((repo/'patches/hwp-fortress-v2-20261026/loadouts.json').read_text());loadouts={r['unit']:r for r in rows}
'''
base=base.replace('for n,a in d[\'assets\'].items():',setup+"\nfor n,a in d['assets'].items():")
exec(compile(base,__file__,'exec'))
