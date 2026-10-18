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
