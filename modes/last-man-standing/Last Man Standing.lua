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
    if self.disabled then
        print('Last Man Standing disabled: no reviewed mission map/site configuration.')
        return
    end
    self.adapter=Adapter.new(Config,Definitions,Scenario)
    self.controller=Core.new(Config)
    self.controller:update(self.adapter:snapshot(),self.adapter)
    self:saveState()
    Objectives:load('LastManStandingObjectives.txt')
    Objectives.visible=true
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
