-- Entry point for a dedicated MMM mission. This mode is not installed in the live game.
include('RescueCore.lua')
include('RescueConfig.lua')
include('NativeAdapter.lua')
include('NativeDefinitions.lua')
include('Scenario.lua')
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
