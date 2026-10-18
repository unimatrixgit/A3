-- MMM 1.0.1 adapter. Must be exercised in a dedicated mission before release.
local Adapter = {}
Adapter.__index = Adapter

function Adapter.new(config, definitions, scenario)
    assert(scenario.sites and scenario.origins, "Map must supply reviewed relocation sites and origins")
    return setmetatable({config=config,definitions=definitions,scenario=scenario},Adapter)
end

function Adapter:snapshot()
    local world = EntityFinder(function(e)
        return e.valid and e:isType(Entity.Type.GameObject) and not e.destroyed
    end):find()
    local snapshot={teams={},sites={},threats={}}
    local teams={}
    for i=1,8 do
        -- Do not query race pointers for empty player slots.
        if self.scenario.origins[i] then
            local p=Player(i)
            local race=p.race.name
            if self.config.factions[race] then
                teams[i]={number=i,race=race,isAI=p.isAI,active=false,
                    constructors=0,structures=0,origin=self.scenario.origins[i]}
                snapshot.teams[#snapshot.teams+1]=teams[i]
            end
        end
    end
    for _,e in pairs(world) do
        local p=e.player
        local team=teams[p.number]
        if team then
            team.active=true
            if self.definitions.builders[e.odf] then team.constructors=team.constructors+1 end
            if self.definitions.structures[e.odf] then team.structures=team.structures+1 end
        end
        if e:isType(Entity.Type.Craft) and p.number>0 then
            local position=e.position
            local threat={x=position.x,z=position.z,enemyTo={}}
            for number in pairs(teams) do
                threat.enemyTo[number]=Player(number):getRelation(p)==Player.Relation.Enemy
            end
            snapshot.threats[#snapshot.threats+1]=threat
        end
    end
    for _,site in ipairs(self.scenario.sites) do
        local inside=site.x-400>=Map.min.x and site.x+400<=Map.max.x
            and site.z-400>=Map.min.z and site.z+400<=Map.max.z
        snapshot.sites[#snapshot.sites+1]={x=site.x,y=site.y or 0,z=site.z,
            validated=site.validated==true and inside,
            resourcesNearby=site.resourcesNearby==true}
    end
    return snapshot
end

function Adapter:deploy(plan)
    local spawned,oldResources={},{}
    local player=Player(plan.player)
    local oldCrew,oldOfficers=player.maxCrew,player.maxOfficers
    local ok,err=pcall(function()
        for name,amount in pairs(plan.resources) do
            oldResources[name]=player.resources[name]
            if name=='crew' then player.maxCrew=math.max(player.maxCrew,amount) end
            if name=='officers' then player.maxOfficers=math.max(player.maxOfficers,amount) end
            player.resources[name]=math.max(player.resources[name],amount)
        end
        for i,odf in ipairs(plan.units) do
            local angle=(i-1)*2*math.pi/#plan.units
            local radius=i==#plan.units and 0 or 250
            local entity=Entity.add(odf,plan.player,Vector(plan.site.x+math.cos(angle)*radius,
                plan.site.y,plan.site.z+math.sin(angle)*radius))
            assert(entity and entity.valid,"Rescue spawn failed: "..odf)
            spawned[#spawned+1]=entity
            assert(entity.player.number==plan.player,"Rescue ownership mismatch")
        end
    end)
    if ok then return true end
    print('Last Man Standing deployment failed: '..tostring(err))
    local complete=true
    for _,entity in ipairs(spawned) do
        local removed=pcall(function() if entity.valid then Entity.remove(entity) end end)
        if not removed then complete=false end
    end
    for name,value in pairs(oldResources) do
        if not pcall(function() player.resources[name]=value end) then complete=false end
    end
    if not pcall(function() player.maxCrew=oldCrew;player.maxOfficers=oldOfficers end) then complete=false end
    if complete then return false end
    return 'indeterminate'
end

LMSNativeAdapter=Adapter
return Adapter
