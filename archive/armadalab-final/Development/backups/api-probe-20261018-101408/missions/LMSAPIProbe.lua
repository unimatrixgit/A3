do local loadModule=function()
LMSRescueConfig={["minimumRelocationDistance"]=2000,["minimumEnemyDistance"]=1200,["factions"]={["federation"]={["hero"]="xhfhero.odf",["constructor"]="fconst.odf",["escorts"]={"fdestroy.odf","fdestroy.odf","fdestroy.odf","fcruise1.odf","fcruise1.odf","fcruise1.odf","fbattle.odf","fbattle.odf","fbattle.odf"},["rebuildResources"]={["dilithium"]=3900,["metal"]=5400,["latinum"]=0,["biomatter"]=0,["crew"]=2400,["officers"]=100},["rebuildPlan"]={"fbase","fmining","forbital","fyard0","fyard","fresear","ffreight","ffreight","fconst"}},["borg"]={["hero"]="blocutus.odf",["constructor"]="bconst.odf",["escorts"]={"bdestroy.odf","bdestroy.odf","bdestroy.odf","bcruise1.odf","bcruise1.odf","bcruise1.odf","bbattle1.odf","bbattle1.odf","bbattle1.odf"},["rebuildResources"]={["dilithium"]=3300,["metal"]=4100,["latinum"]=0,["biomatter"]=0,["crew"]=2100,["officers"]=100},["rebuildPlan"]={"bbase","bmining","bbase2","byard","bresear","bfreight","bfreight","bconst"}},["klingon"]={["hero"]="xhkhero.odf",["constructor"]="kconst.odf",["escorts"]={"kdestroy.odf","kdestroy.odf","kdestroy.odf","kcruise1.odf","kcruise1.odf","kcruise1.odf","kbattle.odf","kbattle.odf","kbattle.odf"},["rebuildResources"]={["dilithium"]=3900,["metal"]=4300,["latinum"]=700,["biomatter"]=0,["crew"]=2100,["officers"]=100},["rebuildPlan"]={"kbase","kmining","korbital","kyard","kresear","kfreight","kfreight","kconst"}},["romulan"]={["hero"]="xhrhero.odf",["constructor"]="rconst.odf",["escorts"]={"rdestroy.odf","rdestroy.odf","rdestroy.odf","rcruise1.odf","rcruise1.odf","rcruise1.odf","rbattle.odf","rbattle.odf","rbattle.odf"},["rebuildResources"]={["dilithium"]=3900,["metal"]=4300,["latinum"]=700,["biomatter"]=0,["crew"]=2100,["officers"]=100},["rebuildPlan"]={"rbase","rmining","rorbital","ryard","rresear","rfreight","rfreight","rconst"}},["cardassian"]={["hero"]="xhchero.odf",["constructor"]="cconst.odf",["escorts"]={"cdestroy.odf","cdestroy.odf","cdestroy.odf","ccruise1.odf","ccruise1.odf","ccruise1.odf","cbattle.odf","cbattle.odf","cbattle.odf"},["rebuildResources"]={["dilithium"]=3900,["metal"]=4300,["latinum"]=700,["biomatter"]=0,["crew"]=2100,["officers"]=100},["rebuildPlan"]={"cbase","cmining","corbital","cyard","cresear","cfreight","cfreight","cconst"}},["dominion"]={["hero"]="xhdhero.odf",["constructor"]="dconst.odf",["escorts"]={"ddestroy.odf","ddestroy.odf","ddestroy.odf","dcruise1.odf","dcruise1.odf","dcruise1.odf","dbattle.odf","dbattle.odf","dbattle.odf"},["rebuildResources"]={["dilithium"]=3900,["metal"]=4900,["latinum"]=0,["biomatter"]=0,["crew"]=2000,["officers"]=100},["rebuildPlan"]={"dbase","dmining","dorbital","dyard","dresear","dfreight","dfreight","dconst"}},["breen"]={["hero"]="xhbrhero.odf",["constructor"]="brconst.odf",["escorts"]={"brdestroy.odf","brdestroy.odf","brdestroy.odf","brcruise1.odf","brcruise1.odf","brcruise1.odf","brbattle.odf","brbattle.odf","brbattle.odf"},["rebuildResources"]={["dilithium"]=3900,["metal"]=4900,["latinum"]=0,["biomatter"]=0,["crew"]=2000,["officers"]=100},["rebuildPlan"]={"brbase","brmining","brorbital","bryard","brresear","brfreight","brfreight","brconst"}},["bajoran"]={["hero"]="bjnerys.odf",["constructor"]="bjconst.odf",["escorts"]={"bjinterceptor.odf","bjinterceptor.odf","bjinterceptor.odf","bjcruiser.odf","bjcruiser.odf","bjcruiser.odf","bjbattle.odf","bjbattle.odf","bjbattle.odf"},["rebuildResources"]={["dilithium"]=3900,["metal"]=4900,["latinum"]=0,["biomatter"]=0,["crew"]=2100,["officers"]=100},["rebuildPlan"]={"bjbase","bjmining","bjorbital","bjyard","bjresear","bjfreight","bjfreight","bjconst"}},["species8472"]={["hero"]="xhshero.odf",["constructor"]="714const.odf",["escorts"]={"8472_destroy.odf","8472_destroy.odf","8472_destroy.odf","8472_cruise1.odf","8472_cruise1.odf","8472_cruise1.odf","8472_battle.odf","8472_battle.odf","8472_battle.odf"},["rebuildResources"]={["dilithium"]=0,["metal"]=0,["latinum"]=0,["biomatter"]=9300,["crew"]=0,["officers"]=100},["rebuildPlan"]={"8472_mothership","8472_transmuter","8472_collector","8472_collector","8472_basicresearch","714const"}}}}
return LMSRescueConfig

end;loadModule() end

do local loadModule=function()
LMSNativeDefinitions={["builders"]={["714const.odf"]=true,["8472_defender.odf"]=true,["bconst.odf"]=true,["bconst2.odf"]=true,["bjconst.odf"]=true,["brconst.odf"]=true,["cconst.odf"]=true,["const.odf"]=true,["dconst.odf"]=true,["domconst.odf"]=true,["f31const.odf"]=true,["fconst.odf"]=true,["fconst2.odf"]=true,["kconst.odf"]=true,["kconst2.odf"]=true,["rconst.odf"]=true,["rconst2.odf"]=true,["uconst.odf"]=true,["xbjuconst.odf"]=true,["xbruconst.odf"]=true,["xbuconst.odf"]=true,["xcuconst.odf"]=true,["xduconst.odf"]=true,["xfuconst.odf"]=true,["xkuconst.odf"]=true,["xruconst.odf"]=true},["structures"]={["714syard.odf"]=true,["714turr.odf"]=true,["8472_advancedresearch.odf"]=true,["8472_basicresearch.odf"]=true,["8472_fluidicgate.odf"]=true,["8472_mine.odf"]=true,["8472_officer.odf"]=true,["8472_sentinel.odf"]=true,["8472_shipupgraderesearch.odf"]=true,["bassturr.odf"]=true,["bbase.odf"]=true,["bbase2.odf"]=true,["bjbase.odf"]=true,["bjmining.odf"]=true,["bjorbital.odf"]=true,["bjresear.odf"]=true,["bjresear2.odf"]=true,["bjsensor.odf"]=true,["bjsuperlab.odf"]=true,["bjtrading.odf"]=true,["bjturret.odf"]=true,["bjturret2.odf"]=true,["bjupgrade.odf"]=true,["bjyard.odf"]=true,["bjyard2.odf"]=true,["bjyard3.odf"]=true,["bmining.odf"]=true,["bomega.odf"]=true,["borbital.odf"]=true,["bportal.odf"]=true,["brbase.odf"]=true,["brecycle.odf"]=true,["bresear.odf"]=true,["bresear2.odf"]=true,["brmining.odf"]=true,["brorbital.odf"]=true,["brresear.odf"]=true,["brresear2.odf"]=true,["bryard.odf"]=true,["bryard2.odf"]=true,["bryard3.odf"]=true,["bsensor.odf"]=true,["bsuperbl.odf"]=true,["btechass.odf"]=true,["bturret.odf"]=true,["bturret2.odf"]=true,["bupgrade.odf"]=true,["byard.odf"]=true,["byard2.odf"]=true,["byard3.odf"]=true,["cardassian_super_station.odf"]=true,["cbase.odf"]=true,["cmining.odf"]=true,["cobyard.odf"]=true,["corbital.odf"]=true,["cquantum.odf"]=true,["cresear.odf"]=true,["cresear2.odf"]=true,["csensor.odf"]=true,["cstation.odf"]=true,["ctrading.odf"]=true,["cturret.odf"]=true,["cturret2.odf"]=true,["cupgrade.odf"]=true,["cyard.odf"]=true,["cyard2.odf"]=true,["cyard3.odf"]=true,["dbase.odf"]=true,["dmining.odf"]=true,["domabase.odf"]=true,["dombase.odf"]=true,["domyard.odf"]=true,["dorbital.odf"]=true,["dresear.odf"]=true,["dresear2.odf"]=true,["ds9.odf"]=true,["dsensor.odf"]=true,["dsuperbl.odf"]=true,["dtrading.odf"]=true,["dturret.odf"]=true,["dturret2.odf"]=true,["dturret3.odf"]=true,["dupgrade.odf"]=true,["dyard.odf"]=true,["dyard2.odf"]=true,["dyard3.odf"]=true,["f6bsuper.odf"]=true,["fargus.odf"]=true,["fbase.odf"]=true,["fbase2.odf"]=true,["fbasehq.odf"]=true,["fbyard.odf"]=true,["fds9.odf"]=true,["fhwp.odf"]=true,["fjupiter.odf"]=true,["fmidas.odf"]=true,["fmining.odf"]=true,["forbital.odf"]=true,["foutpost.odf"]=true,["fregula.odf"]=true,["fremmeler.odf"]=true,["fresear.odf"]=true,["fresear2.odf"]=true,["fsensor.odf"]=true,["fsensor_neutral_zone.odf"]=true,["fsuperbl.odf"]=true,["ftrading.odf"]=true,["fturret.odf"]=true,["fturret2.odf"]=true,["fupgrade.odf"]=true,["fyard.odf"]=true,["fyard0.odf"]=true,["fyard2.odf"]=true,["fyard3.odf"]=true,["hub.odf"]=true,["kbase.odf"]=true,["kbase2.odf"]=true,["khwp.odf"]=true,["kimpbase.odf"]=true,["kimpyard.odf"]=true,["kmarbase.odf"]=true,["kmining.odf"]=true,["korbital.odf"]=true,["koutpost.odf"]=true,["kprison.odf"]=true,["kresear.odf"]=true,["kresear2.odf"]=true,["ksensor.odf"]=true,["ksuperbl.odf"]=true,["ktrading.odf"]=true,["kturret.odf"]=true,["kturret2.odf"]=true,["kupgrade.odf"]=true,["kyard.odf"]=true,["kyard2.odf"]=true,["kyard3.odf"]=true,["orbital.odf"]=true,["rbase.odf"]=true,["rbase2.odf"]=true,["research.odf"]=true,["rhwp.odf"]=true,["rmining.odf"]=true,["rorbital.odf"]=true,["rresear.odf"]=true,["rresear2.odf"]=true,["rsensor.odf"]=true,["rsuperbl.odf"]=true,["rtrading.odf"]=true,["rtsens.odf"]=true,["rturret.odf"]=true,["rturret2.odf"]=true,["rupgrade.odf"]=true,["ryard.odf"]=true,["ryard2.odf"]=true,["ryard3.odf"]=true,["s31yard.odf"]=true,["shield.odf"]=true,["turret.odf"]=true,["xbassimst.odf"]=true,["xbharvest.odf"]=true,["xbomegalab.odf"]=true,["xflegacyyard.odf"]=true,["xfomegalab.odf"]=true,["xhs_yard3.odf"]=true,["zsuperbl.odf"]=true}}
return LMSNativeDefinitions

end;loadModule() end

do local loadModule=function()
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

end;loadModule() end

-- Private diagnostic mission. Wrapped modules are prepended by the staging script.
class 'LMSAPIProbe'
function LMSAPIProbe:__init() self.checked=false end
function LMSAPIProbe:setup() print('LMS API probe: mission entered') end
function LMSAPIProbe:update()
    if self.checked then return end
    self.checked=true
    local stage='entity discovery'
    local ok,err=pcall(function()
        local world=EntityFinder(function(e)
            return e.valid and e:isType(Entity.Type.Craft) and not e.destroyed
        end):find()
        local scenario={origins={},sites={}}
        local anchor
        for _,e in pairs(world) do
            if e.player.number>0 then
                local p=e.position
                scenario.origins[e.player.number]={x=p.x,y=p.y,z=p.z}
                if e.player.number==1 and LMSNativeDefinitions.builders[e.odf] then anchor=e end
            end
        end
        stage='native snapshot'
        local adapter=LMSNativeAdapter.new(LMSRescueConfig,LMSNativeDefinitions,scenario)
        local snapshot=adapter:snapshot()
        assert(#snapshot.teams>0,'no configured factions found')
        stage='owned craft creation'
        assert(anchor and anchor.valid,'no player-one constructor anchor')
        local position=anchor.position
        local craft=Entity.add('fconst.odf',1,Vector(position.x,position.y,position.z))
        assert(craft and craft.valid and craft.player.number==1,'spawn ownership failed')
        stage='owned craft removal'
        Entity.remove(craft)
        stage='save/load stream'
        Save.position=0
        Save:write('LMS.API.1')
        Save:write(true)
        Save:write(11)
        Save:save()
        Load:load()
        Load.position=0
        assert(Load:readString()=='LMS.API.1','string save mismatch')
        assert(Load:readBoolean()==true,'flag save mismatch')
        assert(Load:readNumber()==11,'number save mismatch')
        print('LMS API PASS: '..#snapshot.teams..' teams; owned spawn/removal; save stream')
    end)
    if not ok then print('LMS API FAIL at '..stage..': '..tostring(err)) end
end
MMM.register(LMSAPIProbe())
