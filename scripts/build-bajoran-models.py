"""Create original low-poly Bajoran game adaptations, retaining engine hardpoint names.
SOD serialization: Elenterius/stau, https://github.com/Elenterius/stau (external tool).
"""
import contextlib, copy, io, json, math, pathlib, sys
sys.path.insert(0,'D:/Xaramada-Modwork/tools/stau/src/sod_utils')
from sod_io import SodIO

ROOT=pathlib.Path('D:/armadaIII')
OUT=pathlib.Path('D:/Xaramada-Modwork/bajoran-models')
OUT.mkdir(exist_ok=True)
manifest=json.loads(pathlib.Path('D:/aramada/bajor/manifest.json').read_text())
with contextlib.redirect_stdout(io.StringIO()):
    template=SodIO().read_file(str(ROOT/'SOD/fdestroy.sod'))

identity=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,0.]]
def node(kind,name,parent,data=None,pos=(0,0,0)):
    transform=copy.deepcopy(identity)
    transform[3]=list(pos)
    return dict(type=kind,id=name,parent=parent,local_transform=transform,data=data)

reports=[]
for unit in manifest['units']:
    name=unit['odf']; vertices=[]; coords=[]; triangles=[]
    def polygon(points):
        start=len(vertices)
        vertices.extend([list(v) for v in points])
        # Each component gets a full material tile for consistent panel density.
        coords.extend([[0.,0.],[1.,0.],[1.,1.],[0.,1.]][:len(points)])
        if len(points)>4:
            raise ValueError('Only triangle/quadrilateral faces expected')
        for i in range(1,len(points)-1):
            triangles.append([[start,start],[start+i,start+i],[start+i+1,start+i+1]])
    def box(x,y,z,sx,sy,sz):
        v=[(x+a*sx/2,y+b*sy/2,z+c*sz/2) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(1,2,6,5),(0,4,7,3)]:polygon([v[i] for i in q])
    def wedge(x,y,z,width,height,length):
        # Arrowhead body, positive z is forward.
        v=[(x-width/2,y-height/2,z-length/2),(x+width/2,y-height/2,z-length/2),(x,y-height/2,z+length/2),(x-width/2,y+height/2,z-length/2),(x+width/2,y+height/2,z-length/2),(x,y+height/2,z+length/2)]
        for q in [(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]:polygon([v[i] for i in q])
    def ring(radius,width,y,height,segments=20):
        for i in range(segments):
            a,b=2*math.pi*i/segments,2*math.pi*(i+1)/segments
            def point(angle,r,h):return (math.cos(angle)*r,h,math.sin(angle)*r)
            for q in [[point(a,radius,y-height/2),point(b,radius,y-height/2),point(b,radius,y+height/2),point(a,radius,y+height/2)],
                      [point(a,radius-width,y+height/2),point(b,radius-width,y+height/2),point(b,radius-width,y-height/2),point(a,radius-width,y-height/2)],
                      [point(a,radius-width,y+height/2),point(a,radius,y+height/2),point(b,radius,y+height/2),point(b,radius-width,y+height/2)],
                      [point(a,radius,y-height/2),point(a,radius-width,y-height/2),point(b,radius-width,y-height/2),point(b,radius,y-height/2)]]:polygon(q)
    ship=name in ['bjconst','bjfreight','bjscout','bjinterceptor','bjassault','bjtransport','bjnerys']
    if ship:
        scale=1.35 if name=='bjassault' else 1.
        wedge(0,0,1,9*scale,3,24*scale)
        box(0,2,1,4,2,8)
        for side in [-1,1]:
            wedge(side*9*scale,0,-3,13*scale,1.4,12*scale)
            box(side*15*scale,0,-5,2,2,9)
            box(side*5,0,-10*scale,3,3,5)
        if name in ['bjfreight','bjtransport']:
            for side in [-1,1]:
                for z in [-6,2]:box(side*8,2,z,6,5,7)
        if name=='bjconst':
            box(0,5,-5,22,1,2)
            for side in [-1,1]:box(side*10,2,-5,1,7,2)
        if name=='bjnerys':
            wedge(0,4,-3,3,2,8)
    else:
        ring(7,6,0,4,16)
        box(0,7,0,4,16,4)
        if name in ['bjyard','bjyard2','bjyard3']:
            for side in [-1,1]:
                box(side*18,0,0,3,4,45)
                box(side*18,5,-20,3,12,3)
            box(0,0,-20,36,4,3)
            if name=='bjyard3':ring(27,3,-3,3,24)
            if name=='bjyard2':box(0,8,-20,20,4,5)
        elif name=='bjbase':
            ring(27,4,0,5,24)
            for angle in [0,2*math.pi/3,4*math.pi/3]:
                for r in [8,13,18,23]:box(math.cos(angle)*r,0,math.sin(angle)*r,6,3,6)
                box(math.cos(angle)*25,7,math.sin(angle)*25,4,16,4)
        elif name=='bjmining':
            for x in [-14,14]:
                for z in [-10,10]:box(x,2,z,10,10,10)
        elif name=='bjresear':
            for x in [-13,13]:
                box(x,6,0,2,12,2);wedge(x,12,0,12,1,10)
        else:
            box(0,10,0,8,5,8)
            for x in [-3,3]:box(x,10,8,1.5,1.5,14)
    mesh=dict(texture_material='default',bump_map=0,texture='xbajhull',borgification={'texture':'Bcruise1'},vertices=vertices,texture_coordinates=coords,vertex_lighting_groups=[{'lighting_material':'fdestroy','faces':triangles}],cull_type='NO_CULL')
    nodes=[node('NULL_OR_HARDPOINT','Scene Root',''),node('NULL_OR_HARDPOINT','hardpoints','Scene Root'),node('MESH','BajoranHull','Scene Root',mesh)]
    for i in range(1,100):
        angle=2*math.pi*i/12
        nodes.append(node('NULL_OR_HARDPOINT',f'hp{i:02}','hardpoints',pos=(math.cos(angle)*5,0,math.sin(angle)*8)))
    for i in range(1,10):nodes.append(node('NULL_OR_HARDPOINT',f'pod{i:02}','hardpoints',pos=(0,4,i*2-8)))
    nodes.extend([node('NULL_OR_HARDPOINT','build','hardpoints',pos=(0,0,18)),node('NULL_OR_HARDPOINT','hroot','hardpoints')])
    model=copy.deepcopy(template);model.set_nodes(nodes);model._animation_transforms=[];model._animation_tex_refs=[]
    writer=SodIO();writer.curr_sod_version=model.version
    output=OUT/(name+'.sod')
    with contextlib.redirect_stdout(io.StringIO()):
        writer.write_file(model,str(output));parsed=SodIO().read_file(str(output))
    assert len(parsed.nodes)==len(nodes)
    reports.append({'unit':name,'triangles':len(triangles),'nodes':len(nodes),'roundTripValid':True,'design':'Original low-poly TV-inspired gameplay adaptation','runtimeVerified':False})
    (OUT/(name+'.geometry.json')).write_text(json.dumps({'vertices':vertices,'faces':triangles}))
pathlib.Path('D:/aramada/reports/bajoran-custom-models.json').write_text(json.dumps(reports,indent=2))
print(f'{len(reports)} original Bajoran models generated and round-trip checked in staging; not applied yet.')
