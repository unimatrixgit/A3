-- Private fresh-match rescue prototype. Save/reload is not verified.

(function()
-- Engine-independent rescue rules, compatible with Lua 5.1.
-- Ownership, traversability and resource-site checks are supplied by the map adapter.
local RescueCore = {}
RescueCore.__index = RescueCore

function RescueCore.new(config, saved)
    local self = setmetatable({}, RescueCore)
    self.config = config
    self.teams = saved or {}
    return self
end

local function distance2(a, b)
    return (a.x - b.x)^2 + (a.z - b.z)^2
end

function RescueCore:chooseSite(team, snapshot)
    local state = self.teams[team.number]
    local best, bestDistance
    for _, site in ipairs(snapshot.sites or {}) do
        local valid = site.validated == true and site.resourcesNearby == true
        valid = valid and distance2(site, state.origin) >= self.config.minimumRelocationDistance^2
        for _, threat in ipairs(snapshot.threats or {}) do
            if threat.enemyTo[team.number] and distance2(site, threat) < self.config.minimumEnemyDistance^2 then
                valid = false
            end
        end
        if valid then
            local separation = distance2(site, state.origin)
            if not bestDistance or separation > bestDistance then
                best, bestDistance = site, separation
            end
        end
    end
    return best
end

function RescueCore:update(snapshot, adapter)
    local results = {}
    for _, team in ipairs(snapshot.teams or {}) do
        if team.isAI and team.active and self.config.factions[team.race] then
            local state = self.teams[team.number]
            if not state then
                state = { used=false, seenConstructor=false, pending=false,
                    previousConstructors=team.constructors, origin=team.origin }
                self.teams[team.number] = state
            end
            if team.constructors > 0 then
                state.seenConstructor = true
                state.pending = false
            elseif state.previousConstructors > 0 and state.seenConstructor and not state.used then
                state.pending = true
            end
            state.previousConstructors = team.constructors
            if team.structures <= 0 then state.pending = false end
            if state.pending and not state.used and team.structures > 0 then
                local site = self:chooseSite(team, snapshot)
                if site then
                    local faction = self.config.factions[team.race]
                    local plan = { player=team.number, site=site, units={}, resources=faction.rebuildResources }
                    plan.units[#plan.units+1] = faction.hero
                    for _, escort in ipairs(faction.escorts) do plan.units[#plan.units+1] = escort end
                    plan.units[#plan.units+1] = faction.constructor
                    assert(#faction.escorts == 9 and #plan.units == 11, "Rescue requires exactly eleven craft")
                    -- Reserve before calling engine code: re-entrant updates cannot spawn twice.
                    state.used, state.pending = true, false
                    local ok, committed = pcall(adapter.deploy, adapter, plan)
                    if not ok or committed == "indeterminate" then
                        -- A partial engine rollback could not be verified: never duplicate a fleet.
                        results[#results+1] = { player=team.number, status="deployment_needs_review" }
                    elseif not committed then
                        -- Adapter must roll back partial spawns before returning false.
                        state.used, state.pending = false, true
                        results[#results+1] = { player=team.number, status="deployment_failed" }
                    else
                        results[#results+1] = { player=team.number, status="rescued", plan=plan }
                    end
                else
                    results[#results+1] = { player=team.number, status="waiting_for_safe_site" }
                end
            end
        end
    end
    return results
end

function RescueCore:export()
    local saved = {}
    for number, state in pairs(self.teams) do
        saved[number] = { used=state.used, seenConstructor=state.seenConstructor,
            pending=state.pending, previousConstructors=state.previousConstructors,
            origin={x=state.origin.x, y=state.origin.y, z=state.origin.z} }
    end
    return saved
end

LMSRescueCore=RescueCore
return RescueCore

end)();

(function()
LMSRescueConfig={["minimumRelocationDistance"]=2000,["minimumEnemyDistance"]=1200,["factions"]={["federation"]={["hero"]="xhfhero.odf",["constructor"]="fconst.odf",["escorts"]={"fdestroy.odf","fdestroy.odf","fdestroy.odf","fcruise1.odf","fcruise1.odf","fcruise1.odf","fbattle.odf","fbattle.odf","fbattle.odf"},["rebuildResources"]={["dilithium"]=3900,["metal"]=5400,["latinum"]=0,["biomatter"]=0,["crew"]=2400,["officers"]=100},["rebuildPlan"]={"fbase","fmining","forbital","fyard0","fyard","fresear","ffreight","ffreight","fconst"}},["borg"]={["hero"]="blocutus.odf",["constructor"]="bconst.odf",["escorts"]={"bdestroy.odf","bdestroy.odf","bdestroy.odf","bcruise1.odf","bcruise1.odf","bcruise1.odf","bbattle1.odf","bbattle1.odf","bbattle1.odf"},["rebuildResources"]={["dilithium"]=3300,["metal"]=4100,["latinum"]=0,["biomatter"]=0,["crew"]=2100,["officers"]=100},["rebuildPlan"]={"bbase","bmining","bbase2","byard","bresear","bfreight","bfreight","bconst"}},["klingon"]={["hero"]="xhkhero.odf",["constructor"]="kconst.odf",["escorts"]={"kdestroy.odf","kdestroy.odf","kdestroy.odf","kcruise1.odf","kcruise1.odf","kcruise1.odf","kbattle.odf","kbattle.odf","kbattle.odf"},["rebuildResources"]={["dilithium"]=3900,["metal"]=4300,["latinum"]=700,["biomatter"]=0,["crew"]=2100,["officers"]=100},["rebuildPlan"]={"kbase","kmining","korbital","kyard","kresear","kfreight","kfreight","kconst"}},["romulan"]={["hero"]="xhrhero.odf",["constructor"]="rconst.odf",["escorts"]={"rdestroy.odf","rdestroy.odf","rdestroy.odf","rcruise1.odf","rcruise1.odf","rcruise1.odf","rbattle.odf","rbattle.odf","rbattle.odf"},["rebuildResources"]={["dilithium"]=3900,["metal"]=4300,["latinum"]=700,["biomatter"]=0,["crew"]=2100,["officers"]=100},["rebuildPlan"]={"rbase","rmining","rorbital","ryard","rresear","rfreight","rfreight","rconst"}},["cardassian"]={["hero"]="xhchero.odf",["constructor"]="cconst.odf",["escorts"]={"cdestroy.odf","cdestroy.odf","cdestroy.odf","ccruise1.odf","ccruise1.odf","ccruise1.odf","cbattle.odf","cbattle.odf","cbattle.odf"},["rebuildResources"]={["dilithium"]=3900,["metal"]=4300,["latinum"]=700,["biomatter"]=0,["crew"]=2100,["officers"]=100},["rebuildPlan"]={"cbase","cmining","corbital","cyard","cresear","cfreight","cfreight","cconst"}},["dominion"]={["hero"]="xhdhero.odf",["constructor"]="dconst.odf",["escorts"]={"ddestroy.odf","ddestroy.odf","ddestroy.odf","dcruise1.odf","dcruise1.odf","dcruise1.odf","dbattle.odf","dbattle.odf","dbattle.odf"},["rebuildResources"]={["dilithium"]=3900,["metal"]=4900,["latinum"]=0,["biomatter"]=0,["crew"]=2000,["officers"]=100},["rebuildPlan"]={"dbase","dmining","dorbital","dyard","dresear","dfreight","dfreight","dconst"}},["breen"]={["hero"]="xhbrhero.odf",["constructor"]="brconst.odf",["escorts"]={"brdestroy.odf","brdestroy.odf","brdestroy.odf","brcruise1.odf","brcruise1.odf","brcruise1.odf","brbattle.odf","brbattle.odf","brbattle.odf"},["rebuildResources"]={["dilithium"]=3900,["metal"]=4900,["latinum"]=0,["biomatter"]=0,["crew"]=2000,["officers"]=100},["rebuildPlan"]={"brbase","brmining","brorbital","bryard","brresear","brfreight","brfreight","brconst"}},["bajoran"]={["hero"]="bjnerys.odf",["constructor"]="bjconst.odf",["escorts"]={"bjinterceptor.odf","bjinterceptor.odf","bjinterceptor.odf","bjcruiser.odf","bjcruiser.odf","bjcruiser.odf","bjbattle.odf","bjbattle.odf","bjbattle.odf"},["rebuildResources"]={["dilithium"]=3900,["metal"]=4900,["latinum"]=0,["biomatter"]=0,["crew"]=2100,["officers"]=100},["rebuildPlan"]={"bjbase","bjmining","bjorbital","bjyard","bjresear","bjfreight","bjfreight","bjconst"}},["species8472"]={["hero"]="xhshero.odf",["constructor"]="714const.odf",["escorts"]={"8472_destroy.odf","8472_destroy.odf","8472_destroy.odf","8472_cruise1.odf","8472_cruise1.odf","8472_cruise1.odf","8472_battle.odf","8472_battle.odf","8472_battle.odf"},["rebuildResources"]={["dilithium"]=0,["metal"]=0,["latinum"]=0,["biomatter"]=9300,["crew"]=0,["officers"]=100},["rebuildPlan"]={"8472_mothership","8472_transmuter","8472_collector","8472_collector","8472_basicresearch","714const"}}}}
return LMSRescueConfig

end)();

(function()
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
        local removed=pcall(function()
            if entity.valid then Entity.remove(entity) end
            assert(not entity.valid,'Entity removal could not be verified')
        end)
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

end)();

(function()
LMSNativeDefinitions={["builders"]={["714const.odf"]=true,["8472_defender.odf"]=true,["bconst.odf"]=true,["bconst2.odf"]=true,["bjconst.odf"]=true,["brconst.odf"]=true,["cconst.odf"]=true,["const.odf"]=true,["dconst.odf"]=true,["domconst.odf"]=true,["f31const.odf"]=true,["fconst.odf"]=true,["fconst2.odf"]=true,["kconst.odf"]=true,["kconst2.odf"]=true,["rconst.odf"]=true,["rconst2.odf"]=true,["uconst.odf"]=true,["xbjuconst.odf"]=true,["xbruconst.odf"]=true,["xbuconst.odf"]=true,["xcuconst.odf"]=true,["xduconst.odf"]=true,["xfuconst.odf"]=true,["xkuconst.odf"]=true,["xruconst.odf"]=true},["structures"]={["714syard.odf"]=true,["714turr.odf"]=true,["8472_advancedresearch.odf"]=true,["8472_basicresearch.odf"]=true,["8472_fluidicgate.odf"]=true,["8472_mine.odf"]=true,["8472_officer.odf"]=true,["8472_sentinel.odf"]=true,["8472_shipupgraderesearch.odf"]=true,["bassturr.odf"]=true,["bbase.odf"]=true,["bbase2.odf"]=true,["bjbase.odf"]=true,["bjmining.odf"]=true,["bjorbital.odf"]=true,["bjresear.odf"]=true,["bjresear2.odf"]=true,["bjsensor.odf"]=true,["bjsuperlab.odf"]=true,["bjtrading.odf"]=true,["bjturret.odf"]=true,["bjturret2.odf"]=true,["bjupgrade.odf"]=true,["bjyard.odf"]=true,["bjyard2.odf"]=true,["bjyard3.odf"]=true,["bmining.odf"]=true,["bomega.odf"]=true,["borbital.odf"]=true,["bportal.odf"]=true,["brbase.odf"]=true,["brecycle.odf"]=true,["bresear.odf"]=true,["bresear2.odf"]=true,["brmining.odf"]=true,["brorbital.odf"]=true,["brresear.odf"]=true,["brresear2.odf"]=true,["bryard.odf"]=true,["bryard2.odf"]=true,["bryard3.odf"]=true,["bsensor.odf"]=true,["bsuperbl.odf"]=true,["btechass.odf"]=true,["bturret.odf"]=true,["bturret2.odf"]=true,["bupgrade.odf"]=true,["byard.odf"]=true,["byard2.odf"]=true,["byard3.odf"]=true,["cardassian_super_station.odf"]=true,["cbase.odf"]=true,["cmining.odf"]=true,["cobyard.odf"]=true,["corbital.odf"]=true,["cquantum.odf"]=true,["cresear.odf"]=true,["cresear2.odf"]=true,["csensor.odf"]=true,["cstation.odf"]=true,["ctrading.odf"]=true,["cturret.odf"]=true,["cturret2.odf"]=true,["cupgrade.odf"]=true,["cyard.odf"]=true,["cyard2.odf"]=true,["cyard3.odf"]=true,["dbase.odf"]=true,["dmining.odf"]=true,["domabase.odf"]=true,["dombase.odf"]=true,["domyard.odf"]=true,["dorbital.odf"]=true,["dresear.odf"]=true,["dresear2.odf"]=true,["ds9.odf"]=true,["dsensor.odf"]=true,["dsuperbl.odf"]=true,["dtrading.odf"]=true,["dturret.odf"]=true,["dturret2.odf"]=true,["dturret3.odf"]=true,["dupgrade.odf"]=true,["dyard.odf"]=true,["dyard2.odf"]=true,["dyard3.odf"]=true,["f6bsuper.odf"]=true,["fargus.odf"]=true,["fbase.odf"]=true,["fbase2.odf"]=true,["fbasehq.odf"]=true,["fbyard.odf"]=true,["fds9.odf"]=true,["fhwp.odf"]=true,["fjupiter.odf"]=true,["fmidas.odf"]=true,["fmining.odf"]=true,["forbital.odf"]=true,["foutpost.odf"]=true,["fregula.odf"]=true,["fremmeler.odf"]=true,["fresear.odf"]=true,["fresear2.odf"]=true,["fsensor.odf"]=true,["fsensor_neutral_zone.odf"]=true,["fsuperbl.odf"]=true,["ftrading.odf"]=true,["fturret.odf"]=true,["fturret2.odf"]=true,["fupgrade.odf"]=true,["fyard.odf"]=true,["fyard0.odf"]=true,["fyard2.odf"]=true,["fyard3.odf"]=true,["hub.odf"]=true,["kbase.odf"]=true,["kbase2.odf"]=true,["khwp.odf"]=true,["kimpbase.odf"]=true,["kimpyard.odf"]=true,["kmarbase.odf"]=true,["kmining.odf"]=true,["korbital.odf"]=true,["koutpost.odf"]=true,["kprison.odf"]=true,["kresear.odf"]=true,["kresear2.odf"]=true,["ksensor.odf"]=true,["ksuperbl.odf"]=true,["ktrading.odf"]=true,["kturret.odf"]=true,["kturret2.odf"]=true,["kupgrade.odf"]=true,["kyard.odf"]=true,["kyard2.odf"]=true,["kyard3.odf"]=true,["orbital.odf"]=true,["rbase.odf"]=true,["rbase2.odf"]=true,["research.odf"]=true,["rhwp.odf"]=true,["rmining.odf"]=true,["rorbital.odf"]=true,["rresear.odf"]=true,["rresear2.odf"]=true,["rsensor.odf"]=true,["rsuperbl.odf"]=true,["rtrading.odf"]=true,["rtsens.odf"]=true,["rturret.odf"]=true,["rturret2.odf"]=true,["rupgrade.odf"]=true,["ryard.odf"]=true,["ryard2.odf"]=true,["ryard3.odf"]=true,["s31yard.odf"]=true,["shield.odf"]=true,["turret.odf"]=true,["xbassimst.odf"]=true,["xbharvest.odf"]=true,["xbomegalab.odf"]=true,["xflegacyyard.odf"]=true,["xfomegalab.odf"]=true,["xhs_yard3.odf"]=true,["zsuperbl.odf"]=true}}
return LMSNativeDefinitions

end)();

LMSScenario={["mapId"]="lmstest.bzn",["ready"]=true,["discoverOrigins"]=true,["origins"]={},["sites"]={{["x"]=3000,["y"]=0,["z"]=800,["validated"]=true,["resourcesNearby"]=true},{["x"]=6000,["y"]=0,["z"]=800,["validated"]=true,["resourcesNearby"]=true},{["x"]=3000,["y"]=0,["z"]=8200,["validated"]=true,["resourcesNearby"]=true},{["x"]=6000,["y"]=0,["z"]=8200,["validated"]=true,["resourcesNearby"]=true}}}
-- Entry point for a dedicated MMM mission. This mode is not installed in the live game.
local Core,Config,Adapter=LMSRescueCore,LMSRescueConfig,LMSNativeAdapter
local Definitions,Scenario=LMSNativeDefinitions,LMSScenario

class 'LastManStanding'

function LastManStanding:__init()
    self.disabled=not Scenario.ready
end

function LastManStanding:saveState()
    Save.position=0
    Save:write('ArmadaIII.LastManStanding.1')
    local saved=self.controller:export()
    for i=1,8 do
        local state=saved[i]
        Save:write(state~=nil)
        if state then
            Save:write(state.used)
            Save:write(state.seenConstructor)
            Save:write(state.pending)
            Save:write(state.previousConstructors)
            Save:write(state.origin.x)
            Save:write(state.origin.y)
            Save:write(state.origin.z)
        end
    end
    Save:save()
end

function LastManStanding:setup()
    -- Entity discovery belongs in the first simulation update, not map loading.
    self.pendingSetup=true
end

function LastManStanding:initialize()
    if self.disabled then
        print('Last Man Standing disabled: no reviewed mission map/site configuration.')
        return
    end
    -- Stock Instant Action can call setup on a restored match. Never overwrite
    -- persisted once-only flags merely because MMM did not dispatch resume.
    local ok,helpers=pcall(function()
        return EntityFinder(function(e)
            if not e.valid then return false end
            local odf=string.lower(e.odf or ''):gsub('%.odf$','')
            return odf=='mmm_holder' or odf=='mmm_mapper'
        end):find()
    end)
    if not ok then
        self.disabled=true
        print('Last Man Standing paused: unable to inspect saved-state helpers.')
        return
    end
    if next(helpers)~=nil then
        self:resume()
        return
    end
    if Scenario.discoverOrigins then
        local entities=EntityFinder(function(e)
            return e.valid and e:isType(Entity.Type.Craft) and not e.destroyed
        end):find()
        local priority={}
        for _,e in pairs(entities) do
            local number=e.player.number
            if number>0 and number<=8 then
                local rank=Definitions.structures[e.odf] and 2 or 1
                if rank>(priority[number] or 0) then
                    local p=e.position
                    Scenario.origins[number]={x=p.x,y=p.y,z=p.z}
                    priority[number]=rank
                end
            end
        end
        if next(Scenario.origins)==nil then
            self.disabled=true
            print('Last Man Standing paused: starting fleets were not found.')
            return
        end
    end
    self.adapter=Adapter.new(Config,Definitions,Scenario)
    self.controller=Core.new(Config)
    self.controller:update(self.adapter:snapshot(),self.adapter)
    self:saveState()
    Objectives:load('LastManStandingObjectives.txt')
    Objectives.visible=true
    print('Last Man Standing armed: destroy an AI last constructor; leave a structure intact.')
end

function LastManStanding:resume()
    if self.disabled then return end
    local ok,err=pcall(function()
        Load:load()
        Load.position=0
        assert(Load:readString()=='ArmadaIII.LastManStanding.1','Unknown rescue save schema')
        local saved={}
        for i=1,8 do
            if Load:readBoolean() then
                saved[i]={used=Load:readBoolean(),seenConstructor=Load:readBoolean(),
                    pending=Load:readBoolean(),previousConstructors=Load:readNumber(),
                    origin={x=Load:readNumber(),y=Load:readNumber(),z=Load:readNumber()}}
            end
        end
        self.adapter=Adapter.new(Config,Definitions,Scenario)
        self.controller=Core.new(Config,saved)
    end)
    if not ok then
        self.disabled=true
        print('Last Man Standing paused rather than reset spent rescues: '..tostring(err))
    end
end

function LastManStanding:update()
    if self.pendingSetup then
        self.pendingSetup=false
        self:initialize()
        return
    end
    if self.disabled or not self.controller then return end
    local before=self:stateKey()
    local results=self.controller:update(self.adapter:snapshot(),self.adapter)
    if before~=self:stateKey() then self:saveState() end
    for _,result in ipairs(results) do
        if result.status=='rescued' then
            print('Last Man Standing: reserve task force deployed for player '..result.player)
        end
    end
end

function LastManStanding:stateKey()
    local parts={}
    for i=1,8 do
        local s=self.controller.teams[i]
        if s then
            parts[#parts+1]=i..':'..tostring(s.used)..':'..tostring(s.seenConstructor)
                ..':'..tostring(s.pending)..':'..s.previousConstructors
        end
    end
    return table.concat(parts,';')
end

MMM.register(LastManStanding())
