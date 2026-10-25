"""Share the actual preview geometry with the installable SOD builder."""
import ast
import re,math
from pathlib import Path
_layout_tree=ast.parse(Path('D:/aramada/scripts/preview-yard-family.py').read_text())
_outer=next(x for x in _layout_tree.body if isinstance(x,ast.For)and isinstance(x.target,ast.Tuple))
_inner=next(x for x in _outer.body if isinstance(x,ast.For))
_geometry=[]
for _node in _inner.body:
 if isinstance(_node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='nodes'for t in _node.targets):break
 _geometry.append(_node)
_compiled_layout=compile(ast.Module(body=_geometry,type_ignores=[]),'compact-yard-geometry','exec')
def compact_yard_parts(code,tier,scope):
 env=dict(scope);env.update(code=code,tier=tier)
 exec(_compiled_layout,env)
 variant=scope.get('tier',tier)
 if variant>2:
  # Federation legacy, covert and mirror yards retain their command silhouette
  # but differ in the orientation and placement of their auxiliary hulls.
  for side in [-1,1]:
   env['add'](scope['bases'][code],.18+.035*(variant-2),(side*(.3+.04*variant),.4+.06*variant,-.25),yaw=side*variant*.3)
 return env['parts'],env['bays'],env['cube']
_unit_properties={}
def yard_unit_properties(n,scope,seen=None):
 if n in _unit_properties:return _unit_properties[n]
 seen=set()if seen is None else seen
 if n in seen:raise ValueError('ODF include cycle '+n)
 seen.add(n)
 if 'compactOdfIndex'not in scope:
  scope['compactOdfIndex']={p.stem.lower():p for p in(scope['root']/'odf').rglob('*.odf')}
  scope['compactOdfIndex'].update({p.stem.lower():p for p in(scope['O']/'odf').rglob('*.odf')})
 t=scope['compactOdfIndex'][n].read_text(encoding='latin1');p={}
 for inc in re.findall(r'(?mi)^\s*#include\s+"([^"]+)"',t):p.update(yard_unit_properties(Path(inc).stem.lower(),scope,set(seen)))
 for k,v in re.findall(r'(?mi)^\s*(\w+)\s*=\s*([^\r\n]*)',t):p[k.lower()]=v.split('//')[0].strip().strip('"')
 _unit_properties[n]=p;return p
def fit_yard(n,scope,span,bayScale):
 p=yard_unit_properties(n,scope);ships=[];estimated=[]
 for k,v in p.items():
  if not re.fullmatch('builditem[0-9]+',k):continue
  ship=Path(v).stem.lower();s=yard_unit_properties(ship,scope)
  if s.get('classlabel','').lower()in ['researchpod','researchstation']:continue
  source=s.get('basename',ship).lower();shipScale=abs(float(s.get('scalesod','1').rstrip('fF;')))
  try:
   model=scope['native'](source);points=scope['visible_points'](model)
   points=points[scope['np'].isfinite(points).all(axis=1)]
   assert len(points),(ship,'no finite model bounds')
   extent=scope['np'].ptp(points,axis=0)*shipScale
   diameter=float(max(extent));assert math.isfinite(diameter)and diameter>0,(ship,diameter)
  except (UnicodeError,ValueError,AssertionError,KeyError,IndexError)as e:
   # Some installed legacy SOD variants cannot be decoded by this asset tool.
   # Keep those ships untouched and reserve an explicitly estimated large bay.
   diameter=200*shipScale;estimated.append({'ship':ship,'model':source,'estimatedSpan':diameter,'reason':type(e).__name__})
  ships.append({'ship':ship,'span':diameter})
 largest=max(ships,key=lambda x:x['span'])if ships else{'ship':None,'span':0}
 # Keep a generous margin inside the assembly frame, without changing ships.
 usable=bayScale*.6
 size=max(400,largest['span']*1.25*span/usable)
 return size,{'largestShip':largest,'bayDesignWidth':usable/span*size,'clearanceFactor':1.25,'method':'Conservative model bounding-span estimate','shipsMeasured':len(ships)-len(estimated),'estimatedLegacyModels':estimated}
