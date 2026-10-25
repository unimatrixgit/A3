"""Upgraded faction families. Mesh assembly uses the existing native primitive system."""
import importlib.util,math,numpy as np
from pathlib import Path
sp=importlib.util.spec_from_file_location('base_geometry',Path(__file__).with_name('approved-station-geometry.py'));B=importlib.util.module_from_spec(sp);sp.loader.exec_module(B)

def freighter(race,tier=1):
 g=B.Geometry()
 if race=='federation':
  g.cylinder((0,.05,.44),.42,.13,n=24);g.box((0,0,-.3),(.22,.2,.9))
  for s in [-1,1]:g.box((s*.48,-.1,-.22),(.18,.18,1.2),taper=.8);g.box((s*.48,-.08,-.86),(.16,.1,.09),'glow');g.cylinder((s*.24,.12,-.3),.13,.5,'glow',n=12)
 elif race=='borg':
  g.box((0,0,0),(.7,.5,.9))
  for s in [-1,1]:
   g.box((s*.5,.08,-.25),(.35,.65,.5));g.box((s*.5,-.05,.42),(.3,.35,.45));g.beam((s*.5,.42,-.5),(s*.5,.42,.45),.06,'glow');g.beam((s*.65,-.1,-.65),(s*.65,-.1,.75),.05,'pipes')
 elif race=='klingon':
  g.box((0,.08,.18),(.65,.3,1.2),taper=.55);g.box((0,.13,.76),(.3,.2,.3),taper=.65)
  for s in [-1,1]:g.cylinder((s*.45,-.06,-.25),.24,.58,n=8);g.box((s*.45,-.02,-.4),(.28,.22,.9),taper=.7);g.cylinder((s*.45,.3,-.3),.12,.06,'glow',n=8)
 elif race=='romulan':
  g.sphere((0,0,0),(.26,.23,.85));g.sphere((0,-.22,-.15),(.3,.25,.5))
  for s in [-1,1]:g.box((s*.44,.05,-.13),(.75,.1,.65),yaw=s*.4,taper=.25);g.beam((s*.25,.15,-.65),(s*.8,.05,.3),.08);g.cylinder((s*.73,.05,-.1),.1,.1,'glow',n=8)
 elif race=='cardassian':
  g.box((0,.03,.08),(.37,.3,1.5),taper=.65)
  for s in [-1,1]:
   g.box((s*.45,0,-.15),(.25,.3,1.15),yaw=s*.11,taper=.7);g.beam((s*.15,.1,-.5),(s*.5,.1,.5),.08)
   for z in [-.48,-.16,.16]:g.box((s*.45,.18,z),(.27,.04,.09),'pipes')
 elif race=='dominion':
  g.sphere((0,0,0),(.35,.27,.8))
  for s in [-1,1]:g.sphere((s*.42,-.03,-.2),(.3,.23,.55));g.box((s*.5,.12,.13),(.2,.1,.75),yaw=s*.3,taper=.3);g.sphere((s*.4,.2,-.3),(.13,.07,.23),'glow')
 elif race=='bajoran':
  g.sphere((0,0,0),(.3,.17,.8));g.box((0,.14,.3),(.23,.12,.43),taper=.7)
  for s in [-1,1]:g.torus((0,0,-.05),.56,.09,n=22,start=.1*math.pi,end=.9*math.pi,stretch=(1,.6,1.1));g.sphere((s*.4,-.09,-.15),(.19,.16,.48));g.beam((s*.2,0,-.4),(s*.55,0,.35),.065)
 elif race=='breen':
  g.box((0,0,0),(.5,.4,1.3),taper=.8);g.box((.35,.15,-.2),(.35,.25,.6));g.box((-.37,-.05,.2),(.25,.42,.85));g.box((0,.23,.42),(.24,.16,.4))
  for s in [-1,1]:g.cylinder((s*.32,.05,-.45),.14,.45,'glow',n=8)
 elif race=='ferengi':
  g.sphere((0,.02,0),(.4,.23,.6));g.torus((0,-.02,-.1),.63,.11,n=24,start=.05*math.pi,end=.95*math.pi,stretch=(1,.7,1.1))
  for s in [-1,1]:g.sphere((s*.46,-.02,-.1),(.24,.18,.4));g.cylinder((s*.43,.18,-.2),.13,.05,'glow',n=12)
 else:
  g.sphere((0,0,0),(.33,.28,.8));g.sphere((0,.12,-.35),(.29,.3,.35),'glow')
  for s in [-1,1]:g.torus((s*.12,.02,.2),.45,.07,n=18,start=0,end=.8*math.pi,vertical=True,stretch=(1,.6,1));g.sphere((s*.3,-.12,-.18),(.17,.2,.44))
 # Dedicated emitter housing; mining weapon, rates and capacity stay in the ODF.
 g.cylinder((0,-.05,.82),.1,.12,'pipes',n=10);g.box((0,-.05,.9),(.12,.08,.12),'glow')
 if tier>=2:
  for s in [-1,1]:g.box((s*.22,.25,-.3),(.14,.12,.34),taper=.8)
 if tier>=3:g.torus((0,.2,-.3),.3,.04,'pipes',n=16)
 return g

def refinery(race):
 g=B.Geometry()
 if race=='ferengi':return B.ferengi_station('dilref')
 if race=='species8472':
  g.sphere((0,.12,-.2),(.65,.7,.65));g.sphere((0,.65,-.2),(.38,.35,.4),'glow')
  for s in [-1,1]:g.sphere((s*.62,-.15,.1),(.25,.3,.65));g.torus((0,-.1,.5),.55,.08,n=20,vertical=True,stretch=(1,.75,1))
  return g
 if race=='borg':
  g.box((0,.2,-.2),(1.1,.85,.9))
  for x in [-.6,0,.6]:g.box((x,.32,-.35),(.2,1.15,.45));g.box((x,.9,-.35),(.12,.035,.28),'glow')
 elif race=='federation':
  g.cylinder((0,.1,-.3),.7,.3,n=24);g.cylinder((0,.4,-.3),.45,.28,n=20);g.cylinder((0,.65,-.3),.2,.2,n=16);g.box((0,.85,-.3),(.07,.35,.07))
 elif race=='klingon':
  g.cylinder((0,.1,-.2),.65,.4,n=8,top=.7)
  for x in [-.4,.4]:g.cylinder((x,.65,-.25),.16,.8,n=4,top=.05)
 elif race=='romulan':
  g.sphere((0,.12,-.25),(.45,.32,.6));g.torus((0,0,-.2),.82,.14,n=28,start=0,end=1.25*math.pi,stretch=(1,.6,1))
  for s in [-1,1]:g.box((s*.5,.3,-.3),(.15,.6,.42),yaw=s*.2,taper=.15)
 elif race=='cardassian':
  g.cylinder((0,.1,-.15),.5,.25,n=12);g.cylinder((0,.6,-.15),.12,.95,n=4,top=.08)
  for a in [0,2*math.pi/3,4*math.pi/3]:g.box((.55*math.sin(a),.02,.55*math.cos(a)-.15),(.35,.3,.95),yaw=a,taper=.7)
 elif race=='dominion':
  g.sphere((0,.15,-.3),(.5,.37,.5))
  for a in [0,2*math.pi/3,4*math.pi/3]:g.sphere((.48*math.sin(a),.1,.48*math.cos(a)-.3),(.36,.24,.45))
 elif race=='bajoran':
  g.sphere((0,.17,-.3),(.5,.25,.55));g.torus((0,0,-.1),.8,.1,n=26,start=.15*math.pi,end=1.25*math.pi,stretch=(1,.65,1))
 else:g.box((0,.2,-.25),(1.1,.65,.75),taper=.7);g.box((.5,.4,-.25),(.4,.4,.6));g.box((-.45,.1,-.45),(.3,.7,.55))
 for x in [-.48,.48]:
  g.box((x,-.2,.38),(.2,.15,1.18),'dark');g.box((x,-.1,.48),(.06,.035,.9),'glow');g.beam((x,-.2,.55),(x,.46,.55),.065);g.beam((x,.46,.55),(x,.46,-.3),.05)
  g.cylinder((x,.52,.55),.12,.1,'hull',n=12)
 return g

def research(race,count=6,variant=1):
 g=B.Geometry();g.mounts=[]
 if race=='federation':g.cylinder((0,0,0),.48,.2,n=24);g.sphere((0,.22,0),(.36,.32,.36),'glow')
 elif race=='borg':g.box((0,.08,0),(.62,.62,.62));g.box((0,.57,0),(.2,.5,.2));g.beam((-.32,.4,-.3),(.32,.4,.3),.04,'glow')
 elif race=='klingon':g.cylinder((0,.04,0),.46,.35,n=8,top=.7);g.cylinder((0,.65,0),.14,.95,n=4,top=.05)
 elif race=='romulan':g.sphere((0,.1,0),(.4,.24,.5));g.torus((0,.04,0),.49,.055,n=24,start=0,end=1.5*math.pi);g.cylinder((0,.58,-.1),.08,.8,n=4,top=.1)
 elif race=='cardassian':g.cylinder((0,0,0),.43,.25,n=12);g.cylinder((0,.58,0),.1,1.0,n=4,top=.08)
 elif race=='dominion':
  g.sphere((0,.08,0),(.48,.3,.42))
  for s in [-1,1]:g.sphere((s*.24,.18,-.15),(.23,.22,.38),'glow')
 elif race=='bajoran':g.torus((0,.02,0),.42,.1,n=24,stretch=(1,.6,1));g.sphere((0,.1,-.25),(.3,.22,.3));g.cylinder((0,.4,-.25),.08,.4,n=6,top=.05)
 elif race=='breen':g.box((0,.1,0),(.65,.5,.55),taper=.8);g.box((.25,.42,-.2),(.23,.32,.35));g.box((-.2,.32,.2),(.23,.22,.3),'glow')
 elif race=='ferengi':g.sphere((0,.05,0),(.5,.28,.44));g.torus((0,-.04,0),.52,.07,n=24);g.sphere((0,.28,0),(.17,.12,.17),'glow')
 else:g.sphere((0,.08,0),(.4,.4,.45));g.sphere((0,.43,0),(.2,.23,.2),'glow')
 # Every socket has a real geometric mount and is associated with the native pod ID.
 for i in range(count):
  a=i*math.tau/max(count,1);r=.98 if race!='bajoran'else .94;pos=np.array([r*math.sin(a),0,r*math.cos(a)]);g.mounts.append(tuple(pos))
  g.beam(pos*.35,pos,.065,'pipes');g.beam(pos*.38+[0,.055,0],pos+[0,.055,0],.025,'glow')
  if race=='borg':g.box(pos,(.25,.15,.25));g.box(pos+[0,.09,0],(.18,.025,.18),'glow')
  elif race=='species8472':g.sphere(pos,(.18,.12,.2));g.torus(pos+[0,.1,0],.12,.025,'glow',n=12)
  elif race in ['klingon','breen']:g.cylinder(pos,.18,.14,n=6);g.torus(pos+[0,.09,0],.13,.02,'glow',n=12)
  else:g.cylinder(pos,.18,.12,n=12);g.torus(pos+[0,.08,0],.13,.02,'glow',n=16)
 if variant>=2:
  for x in [-.22,.22]:g.cylinder((x,.58,-.13),.05,.6,n=6,top=.2)
 if variant>=3:g.torus((0,.3,0),.29,.04,'glow',n=18)
 return g

def assimilation(kind='turret',count=0):
 g=B.Geometry();g.mounts=[]
 # Shared lattice core and four radial assimilation-emitter shoulders.
 g.box((0,.12,-.12),(.7,.65,.7));g.box((0,.6,-.12),(.33,.55,.33));g.box((0,.91,-.12),(.22,.045,.22),'glow')
 shoulders=[(-.62,0),(.62,0),(0,-.7)]+([]if kind=='producer'else[(0,.58)])
 for x,z in shoulders:
  g.beam((0,.05,-.12),(x,.05,z),.16);g.box((x,.15,z),(.34,.45,.35));g.box((x,.4,z),(.24,.035,.25),'glow')
  for yy in [-.02,.2]:g.box((x,yy,z),(.37,.04,.37),'dark')
  g.beam((x,.4,z),(x,.65,z),.055,'pipes')
 if kind=='producer':
  # Repair-drone production has a genuinely open bay and a matching build anchor.
  for x in [-.4,.4]:g.box((x,-.17,.63),(.16,.15,.88),'dark');g.beam((x,-.2,.3),(x,.33,.3),.06);g.box((x,-.05,.7),(.035,.035,.68),'glow')
  g.beam((-.4,.33,.3),(.4,.33,.3),.065);g.build=(0,-.04,.76)
 for i in range(count):
  a=(i+.5)*math.tau/max(count,1);pos=np.array([.95*math.sin(a),-.08,.95*math.cos(a)-.12]);g.mounts.append(tuple(pos));g.beam((0,-.1,-.12),pos,.06,'pipes');g.box(pos,(.25,.13,.25));g.box(pos+[0,.08,0],(.18,.02,.18),'glow')
 return g

def recycler():
 g=B.Geometry()
 for x in [-.68,.68]:
  g.box((x,0,0),(.34,.78,1.7));g.beam((x,.45,-.8),(x,.45,.8),.05,'glow')
  for z in [-.6,0,.6]:g.box((x,.44,z),(.3,.18,.24));g.box((x-.15*(1 if x>0 else-1),.1,z),(.1,.1,.2),'glow')
  g.beam((x,-.38,-.7),(x,-.38,.7),.06,'pipes')
 for z in [-.65,.65]:g.beam((-.68,.4,z),(.68,.4,z),.16);g.beam((-.68,-.4,z),(.68,-.4,z),.12)
 for x in [-.42,.42]:g.beam((x,.28,-.4),(x*.7,.06,0),.05,'pipes');g.box((x*.7,.02,0),(.1,.18,.18),'glow')
 g.box((.93,.05,-.43),(.22,.45,.6));g.box((-.93,-.05,.22),(.22,.5,.65));return g

def repair_drone():
 g=B.constructor('borg',1)
 for x,z in [(-.65,-.25),(.65,-.25),(-.75,.45),(.75,.45)]:
  g.beam((x*.45,.08,z*.5),(x,.16,z),.055,'pipes');g.box((x,.15,z),(.16,.12,.18));g.box((x,.15,z+.1),(.13,.08,.05),'glow')
 g.sphere((0,.3,-.3),(.15,.12,.2),'glow',n=12,m=6);return g
