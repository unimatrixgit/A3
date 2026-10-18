local Core = assert(loadfile(ROOT .. '/RescueCore.lua'))()
local Config = assert(loadfile(ROOT .. '/RescueConfig.lua'))()
local count = 0
local function test(name, body)
    body()
    count = count + 1
end
local function team(n, constructors, structures, isAI)
    return {number=n or 2, race='borg', constructors=constructors or 0,
        structures=structures or 1, isAI=isAI~=false, active=true,
        origin={x=0,y=0,z=0}}
end
local safe={x=3000,y=0,z=3000,validated=true,resourcesNearby=true}
local function snapshot(teams, sites, threats)
    return {teams=teams,sites=sites or {safe},threats=threats or {}}
end
local function adapter()
    return {calls={},deploy=function(self,plan)
        self.calls[#self.calls+1]=plan
        return true
    end}
end
local function armed()
    local c,a=Core.new(Config),adapter()
    c:update(snapshot({team(2,1)}),a)
    return c,a
end

test('No rescue at start without prior constructor',function()
    local c,a=Core.new(Config),adapter()
    c:update(snapshot({team(2,0)}),a)
    assert(#a.calls==0)
end)
test('Last constructor loss deploys eleven craft',function()
    local c,a=armed()
    c:update(snapshot({team(2,0)}),a)
    assert(#a.calls==1 and #a.calls[1].units==11)
    assert(a.calls[1].units[1]=='blocutus.odf')
    assert(a.calls[1].units[11]=='bconst.odf')
end)
test('Each AI receives only one rescue',function()
    local c,a=armed()
    c:update(snapshot({team(2,0)}),a)
    c:update(snapshot({team(2,1)}),a)
    c:update(snapshot({team(2,0)}),a)
    assert(#a.calls==1)
end)
test('Human excluded',function()
    local c,a=Core.new(Config),adapter()
    c:update(snapshot({team(1,1,1,false)}),a)
    c:update(snapshot({team(1,0,1,false)}),a)
    assert(#a.calls==0)
end)
test('No rescue after final structure lost',function()
    local c,a=armed()
    c:update(snapshot({team(2,0,0)}),a)
    assert(#a.calls==0)
end)
test('Never reuse starting location',function()
    local c,a=armed()
    c:update(snapshot({team(2,0)},{{x=100,y=0,z=0,validated=true,resourcesNearby=true}}),a)
    assert(#a.calls==0)
end)
test('Enemy presence defers rescue',function()
    local c,a=armed()
    c:update(snapshot({team(2,0)},nil,{{x=3000,z=3000,enemyTo={[2]=true}}}),a)
    assert(#a.calls==0 and c.teams[2].pending)
    c:update(snapshot({team(2,0)}),a)
    assert(#a.calls==1)
end)
test('Unvalidated or resource-free sites rejected',function()
    local c,a=armed()
    c:update(snapshot({team(2,0)},{{x=4000,z=4000,validated=false,resourcesNearby=true},
        {x=5000,z=5000,validated=true,resourcesNearby=false}}),a)
    assert(#a.calls==0)
end)
test('AI constructor recovery cancels pending rescue',function()
    local c,a=armed()
    c:update(snapshot({team(2,0)},{}),a)
    c:update(snapshot({team(2,1)}),a)
    assert(#a.calls==0 and not c.teams[2].pending)
end)
test('Used flag survives core export and restoration',function()
    local c,a=armed()
    c:update(snapshot({team(2,0)}),a)
    local restored=Core.new(Config,c:export())
    restored:update(snapshot({team(2,0)}),a)
    assert(#a.calls==1)
end)
test('Rescue flags independent per AI',function()
    local c,a=Core.new(Config),adapter()
    c:update(snapshot({team(2,1),team(3,1)}),a)
    c:update(snapshot({team(2,0),team(3,0)}),a)
    assert(#a.calls==2 and c.teams[2].used and c.teams[3].used)
end)
test('Failed transactional deployment can retry',function()
    local c,a=armed()
    a.deploy=function() return false end
    c:update(snapshot({team(2,0)}),a)
    assert(not c.teams[2].used and c.teams[2].pending)
    a=adapter()
    c:update(snapshot({team(2,0)}),a)
    assert(#a.calls==1)
end)
test('All nine factions have complete rescue packages',function()
    local n=0
    for race,f in pairs(Config.factions) do
        assert(#f.escorts==9 and f.hero and f.constructor)
        assert(f.rebuildResources.crew>0 or race=='species8472')
        n=n+1
    end
    assert(n==9)
end)
return count
