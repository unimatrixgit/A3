"""Approved structural families. Geometry coordinates are normalized, independent of gameplay stats."""
import numpy as np,math
class Geometry:
 def __init__(self):self.parts=[]
 def add(self,v,f,mat='hull'):
  self.parts.append({'v':np.asarray(v,float),'f':f,'mat':mat})
 def box(self,pos,size,mat='hull',yaw=0,taper=1):
  x,y,z=size;v=np.array([[-x/2,-y/2,-z/2],[x/2,-y/2,-z/2],[x/2,-y/2,z/2],[-x/2,-y/2,z/2],[-x*taper/2,y/2,-z*taper/2],[x*taper/2,y/2,-z*taper/2],[x*taper/2,y/2,z*taper/2],[-x*taper/2,y/2,z*taper/2]])
  a=yaw;rot=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]]);v=v@rot.T+pos;self.add(v,[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)],mat)
 def cylinder(self,pos,radius,height,mat='hull',n=16,top=1):
  v=[]
  for y,r in [(-height/2,radius),(height/2,radius*top)]:
   for i in range(n):a=i*math.tau/n;v.append([pos[0]+r*math.cos(a),pos[1]+y,pos[2]+r*math.sin(a)])
  v+=[[pos[0],pos[1]-height/2,pos[2]],[pos[0],pos[1]+height/2,pos[2]]];f=[]
  for i in range(n):j=(i+1)%n;f +=[(i,j,n+j),(i,n+j,n+i),(2*n,j,i),(2*n+1,n+i,n+j)]
  self.add(v,f,mat)
 def torus(self,pos,radius,tube,mat='hull',n=24,m=6,start=0,end=math.tau,vertical=False,stretch=(1,1,1)):
  v=[]
  for i in range(n+1):
   a=start+(end-start)*i/n
   for j in range(m):
    b=j*math.tau/m;q=[(radius+tube*math.cos(b))*math.cos(a),tube*math.sin(b),(radius+tube*math.cos(b))*math.sin(a)]
    if vertical:q=[q[0],q[2],q[1]]
    v.append(np.asarray(q)*stretch+pos)
  f=[]
  for i in range(n):
   for j in range(m):a=i*m+j;b=i*m+(j+1)%m;c=(i+1)*m+(j+1)%m;d=(i+1)*m+j;f +=[(a,b,c),(a,c,d)]
  self.add(v,f,mat)
 def sphere(self,pos,size,mat='hull',n=16,m=8):
  v=[]
  for j in range(m+1):
   b=math.pi*j/m
   for i in range(n):a=i*math.tau/n;v.append(np.asarray([math.sin(b)*math.cos(a),math.cos(b),math.sin(b)*math.sin(a)])*size+pos)
  f=[]
  for j in range(m):
   for i in range(n):a=j*n+i;b=j*n+(i+1)%n;c=(j+1)*n+(i+1)%n;d=(j+1)*n+i;f +=[(a,b,c),(a,c,d)]
  self.add(v,f,mat)
 def beam(self,a,b,width=.07,mat='dark'):
  a=np.asarray(a);b=np.asarray(b);mid=(a+b)/2;vec=b-a;length=np.linalg.norm(vec);temp=Geometry();temp.box((0,0,0),(width,width,length),mat);z=vec/length;x=np.cross([0,1,0],z)
  if np.linalg.norm(x)<.01:x=np.cross([1,0,0],z)
  x/=np.linalg.norm(x);y=np.cross(z,x);rot=np.array([x,y,z]).T
  for p in temp.parts:p['v']=p['v']@rot.T+mid;self.parts.append(p)

def orbital(race,tier=1):
 g=Geometry();g.cylinder((0,0,0),.54,.63,n=24);g.cylinder((0,.37,0),.4,.12);g.cylinder((0,.5,0),.17,.18)
 for yy in [-.27,.2]:g.torus((0,yy,0),.6,.08,'dark');g.torus((0,yy+.03,0),.59,.025,'glow')
 for i in range(4):
  a=i*math.pi/2;direction=np.array([math.cos(a),0,math.sin(a)]);pos=direction*1.03
  g.beam(direction*.45, direction*1.18,.13);g.beam(direction*.45+[0,-.17,0],direction*1.12+[0,-.17,0],.055,'pipes')
  if race in ['ferengi','romulan']:g.sphere(pos,(.36,.23,.29))
  else:g.box(pos,(.42,.4,.5),yaw=a,taper=.88 if race in ['klingon','dominion','breen']else 1)
  for t in [-.12,.12]:g.box(pos+[0,t,0],(.44,.025,.52),'dark',yaw=a)
  g.cylinder(direction*.65+[0,.15,0],.08,.48,'pipes',n=10)
  if race in ['klingon','dominion']:g.cylinder(pos+[0,.36,0],.1,.35,n=4,top=.05)
  elif race=='borg':
   for sign in [-1,1]:g.box(pos+[0,.27,sign*.14],(.08,.32,.08),'glow')
  elif race in ['bajoran','romulan','ferengi']:g.torus(pos,.3,.045,n=12,start=0,end=math.pi,stretch=(1,.7,1))
 for xx in [-.2,.2]:g.cylinder((xx,-.65,0),.12,.7,'pipes',n=12);g.cylinder((xx,-1.0,0),.14,.07,'glow',n=12)
 for i in range(8):a=i*math.tau/8;g.box((.55*math.cos(a),.02,.55*math.sin(a)),(.05,.28,.09),'glow',yaw=-a)
 if tier>=2:
  g.torus((0,.5,0),.35,.045,'dark')
  for a in [math.pi/4,math.pi*1.25]:g.cylinder((.7*math.cos(a),.12,.7*math.sin(a)),.1,.45,'hull',n=10)
 return g

def yard(race,tier=1,service=False):
 g=Geometry();tier=max(1,min(tier,3))
 if race=='species8472':
  for zz in [-.75,0,.75][:tier+1]:g.torus((0,0,zz),.95,.11,n=28,vertical=True,stretch=(1,.7,1));g.torus((0,0,zz+.05),.81,.035,'glow',n=24,vertical=True,stretch=(1,.7,1))
  for sign in [-1,1]:
   g.sphere((sign*.85,-.27,0),(.2,.26,1.1));g.beam((sign*.8,-.4,-1.15),(sign*.8,.3,1.1),.075)
   for z in [-.7,-.25,.25,.7]:g.sphere((sign*.92,.12,z),(.18,.3,.14))
  return g
 for x in [-.9,.9]:
  g.box((x,-.3,0),(.26,.22,2.3),'dark');g.box((x,.02,-.3),(.24,.35,1.55),taper=.8)
  for z in [-.85,.3,.85]:
   g.cylinder((x,.3,z),.14,.75,n=8,top=.8);g.box((x,.16,z),(.3,.045,.15),'glow')
   for y in [-.25,.15]:g.beam((x,y,z),(x*.65,y,z),.035,'pipes')
  g.beam((x,.58,-.85),(x,.58,.85),.065)
 g.box((0,.03,-1.0),(1.9,.32,.3));g.beam((-.9,.58,-.85),(.9,.58,-.85),.06,'dark')
 for x in [-.55,.55]:g.box((x,-.38,.4),(.04,.06,1.65),'glow')
 if race=='borg':
  for x in [-1.03,1.03]:
   for z in [-.9,-.3,.3,.9]:g.box((x,.24,z),(.14,.5,.12));g.box((x,.29,z),(.15,.24,.035),'glow')
   g.beam((x,-.15,-1),(x,.6,.9),.04,'dark')
 elif race in ['romulan','cardassian','ferengi','bajoran']:
  g.torus((0,.12,-.05),1.04,.13,n=32,start=0,end=math.pi*1.12,stretch=(1,.6,1.15))
  for x in [-1,1]:g.sphere((x,.08,-.05),(.22,.15,1.02))
 elif race in ['klingon','dominion']:
  for x in [-1,1]:
   g.box((x,.18,0),(.36,.44,1.85),yaw=x*.1,taper=.65);g.cylinder((x,.78,-.8),.16,.8,n=4,top=.05)
 elif race=='breen':
  for x in [-1,1]:g.box((x,.12,0),(.4,.42,2),taper=.8);g.box((x,.15,.7),(.44,.09,.15),'glow')
 else:
  for x in [-1,1]:g.torus((x,.05,.58),.28,.08,n=16,vertical=True,stretch=(1,.8,1));g.cylinder((x,.65,-.85),.23,.08,n=16)
 if tier>=2:
  for x in [-1.05,1.05]:g.box((x,.17,-.85),(.38,.7,.45),taper=.8);g.cylinder((x,.8,-.85),.13,.6,n=8,top=.7)
 if tier>=3:
  g.box((0,.3,-1.05),(.65,.55,.35));g.cylinder((0,.92,-1.05),.12,.8,n=6,top=.3)
  for x in [-1.15,1.15]:g.box((x,.3,.48),(.4,.7,.48),taper=.8)
 if service:
  for x in [-.55,.55]:g.cylinder((x,-.15,-1.3),.17,.42,'pipes',n=12)
 return g

def ferengi_station(kind):
 g=Geometry();g.sphere((0,.1,-.2),(.68,.32,.65));g.cylinder((0,-.1,-.2),.66,.2,n=24);g.torus((0,.02,-.2),.69,.04,'glow')
 g.torus((0,-.12,.12),1.0,.16,n=32,start=math.pi*.12,end=math.pi*1.88,stretch=(1,.7,1.1))
 for x in [-.5,.5]:g.beam((x*.5,0,-.3),(x*1.8,-.12,.3),.09,'pipes')
 for x in [-.45,0,.45]:
  g.cylinder((x,.35,-.7),.11,.6,'glow',n=12);g.cylinder((x,.68,-.7),.15,.07,n=12);g.cylinder((x,.02,-.7),.15,.07,n=12)
 if kind=='research':
  for i in range(4):a=i*math.tau/4;g.cylinder((.85*math.cos(a),.25,.85*math.sin(a)),.2,.4,n=12)
  g.sphere((0,.55,-.2),(.25,.27,.25),'glow')
 else:
  for x in [-1,1]:g.box((x,-.05,.45),(.24,.28,.35));g.box((x,.02,.61),(.14,.11,.025),'glow')
 return g

def constructor(race,tier=1):
 g=Geometry()
 if race=='species8472':
  g.sphere((0,0,0),(.36,.25,.75));g.sphere((0,.05,.65),(.25,.2,.3))
  for x in [-1,1]:
   g.torus((x*.18,0,.2),.45,.045,n=18,start=0,end=math.pi*.8,vertical=True,stretch=(1,.7,1));g.sphere((x*.3,-.05,-.3),(.12,.15,.45),'glow')
 else:
  if race in ['ferengi','bajoran','cardassian']:g.sphere((0,0,-.1),(.42,.18,.75))
  else:g.box((0,0,-.1),(.55,.32,1.35),taper=.7 if race in ['romulan','klingon','dominion']else 1)
  g.box((0,.2,-.3),(.28,.18,.36),'glow')
  for side in [-1,1]:
   g.beam((side*.2,-.05,.1),(side*.55,-.12,.65),.065);g.box((side*.55,-.1,.7),(.12,.12,.32),'pipes');g.box((side*.55,-.1,.9),(.14,.09,.07),'glow')
   if race=='federation':g.cylinder((side*.55,0,-.35),.12,.35,n=12);g.box((side*.55,0,-.4),(.16,.15,.7));g.box((side*.55,.01,-.73),(.16,.1,.1),'glow')
   elif race=='borg':
    g.box((side*.43,0,-.25),(.24,.4,1.2));g.beam((side*.5,.25,-.7),(side*.5,.25,.45),.05,'glow')
   elif race in ['romulan','klingon','dominion']:g.box((side*.6,-.04,-.15),(.65,.12,.4),yaw=side*.25,taper=.55);g.cylinder((side*.82,.02,-.25),.09,.2,'glow',n=6)
   elif race in ['ferengi','cardassian','bajoran']:g.torus((0,-.05,-.1),.65,.08,n=20,start=.15*math.pi,end=.85*math.pi,stretch=(1,.6,1.1));g.sphere((side*.5,-.05,-.2),(.2,.13,.55))
   else:g.box((side*.5,-.04,-.3),(.25,.28,.8),taper=.75)
 if tier>=2:
  for x in [-.28,.28]:g.box((x,.26,-.3),(.18,.15,.5));g.box((x,.36,-.3),(.1,.035,.3),'glow')
 if tier>=3:g.torus((0,.17,-.2),.39,.045,n=18,vertical=True);g.sphere((0,.47,-.2),(.1,.13,.12),'glow')
 return g

