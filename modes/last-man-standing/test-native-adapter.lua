local Adapter=assert(loadfile(ROOT..'/NativeAdapter.lua'))()
local Definitions=assert(loadfile(ROOT..'/NativeDefinitions.lua'))()
local Config=assert(loadfile(ROOT..'/RescueConfig.lua'))()
local count=0
local players,world,created,removed,failAt,wrongOwner,removeFails
local function reset()
    players,world,created,removed={}, {}, {}, {}
    failAt,wrongOwner,removeFails=nil,false,false
    for i=1,8 do
        players[i]={number=i,isAI=i~=1,race={name='borg'},maxCrew=2000,maxOfficers=100,
            resources={crew=100,officers=2,dilithium=100,metal=50,biomatter=0,latinum=0},
            getRelation=function(self,other) return self.number==other.number and 0 or 2 end}
    end
    Player=setmetatable({Relation={Enemy=2}}, {__call=function(_,i)return players[i]end})
    Vector=function(x,y,z)return{x=x,y=y,z=z}end
    Map={min=Vector(-10000,0,-10000),max=Vector(10000,0,10000)}
    Entity={Type={GameObject=1,Craft=2}}
    Entity.add=function(odf,owner,position)
        if failAt and #created+1==failAt then return nil end
        local e={valid=true,odf=odf,player=players[wrongOwner and 1 or owner],position=position}
        created[#created+1]=e
        return e
    end
    Entity.remove=function(e)
        if removeFails then error('simulated removal failure')end
        e.valid=false;removed[#removed+1]=e
    end
    EntityFinder=function(predicate)
        return {find=function()
            local out={}
            for _,e in ipairs(world)do if predicate(e)then out[#out+1]=e end end
            return out
        end}
    end
end
local scenario={origins={[1]={x=0,y=0,z=0},[2]={x=8000,y=0,z=8000}},
    sites={{x=4000,y=0,z=4000,validated=true,resourcesNearby=true}}}
local function plan()
    local f=Config.factions.borg
    local units={f.hero}
    for _,u in ipairs(f.escorts)do units[#units+1]=u end
    units[#units+1]=f.constructor
    return{player=2,site=scenario.sites[1],units=units,
        resources={crew=3000,officers=20,dilithium=5000,metal=4000,biomatter=0,latinum=0}}
end
local function test(name,fn) reset();fn();count=count+1 end
test('Owned full fleet and funds',function()
    local a=Adapter.new(Config,Definitions,scenario)
    assert(a:deploy(plan())==true and #created==11)
    for _,e in ipairs(created)do assert(e.player.number==2)end
    assert(players[2].resources.dilithium==5000 and players[2].maxCrew>=3000)
end)
test('Partial spawn fails without duplicate fleet or lost funds',function()
    failAt=6
    assert(Adapter.new(Config,Definitions,scenario):deploy(plan())==false)
    assert(#created==5 and #removed==5)
    assert(players[2].resources.dilithium==100 and players[2].resources.metal==50)
    assert(players[2].maxCrew==2000)
end)
test('Wrong ownership removes mismatched entity',function()
    wrongOwner=true
    assert(Adapter.new(Config,Definitions,scenario):deploy(plan())==false)
    assert(#created==1 and #removed==1)
end)
test('Unverified rollback fails closed',function()
    failAt=3;removeFails=true
    assert(Adapter.new(Config,Definitions,scenario):deploy(plan())=='indeterminate')
end)
test('Never reduce existing player resources',function()
    players[2].resources.dilithium=9999
    assert(Adapter.new(Config,Definitions,scenario):deploy(plan())==true)
    assert(players[2].resources.dilithium==9999)
end)

test('Silent or deferred removal cannot permit another rescue',function()
    failAt=3
    Entity.remove=function() end
    assert(Adapter.new(Config,Definitions,scenario):deploy(plan())=='indeterminate')
end)
test('Map-edge relocation area rejected',function()
    local edge={origins=scenario.origins,sites={{x=9900,z=9900,validated=true,resourcesNearby=true}}}
    local snap=Adapter.new(Config,Definitions,edge):snapshot()
    assert(not snap.sites[1].validated)
end)
test('Invalid entity ignored before property access',function()
    world={{valid=false,isType=function()error('invalid entity read')end}}
    assert(#Adapter.new(Config,Definitions,scenario):snapshot().threats==0)
end)
test('Research pods and terrain do not keep an eliminated base alive',function()
    assert(not Definitions.structures['fedpod1.odf'])
    assert(not Definitions.structures['pb_earth.odf'])
    assert(not Definitions.structures['scrap.odf'])
    assert(Definitions.structures['fbase.odf'] and Definitions.structures['bjmining.odf'])
end)
return count
