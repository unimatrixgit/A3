-- Regression: setup after a native reload must not reset spent rescues.
local count=0
local function run(name,helpers,loadError,expectedResume,expectedSave)
    local registered
    include=function() end
    class=function(name)
        local c={};c.__index=c
        setmetatable(c,{__call=function(t)
            local o=setmetatable({},t);o:__init();return o
        end});_G[name]=c
    end
    LMSScenario={ready=true};LMSRescueConfig={};LMSNativeDefinitions={}
    LMSNativeAdapter={new=function() return {snapshot=function()return {}end}end}
    LMSRescueCore={new=function()return {update=function()end}end}
    MMM={register=function(o) registered=o end}
    Objectives={load=function()end}
    print=function()end
    EntityFinder=function(predicate)
        return {find=function()
            if helpers=='error' then error('finder unavailable') end
            local found={}
            for _,e in ipairs(helpers)do if predicate(e)then found[#found+1]=e end end
            return found
        end}
    end
    assert(loadfile(ROOT..'/Last Man Standing.lua'))()
    local resumes,saves=0,0
    registered.resume=function(self)
        resumes=resumes+1
        if loadError then self.disabled=true end
    end
    registered.saveState=function()saves=saves+1 end
    registered:setup()
    assert(resumes==0 and saves==0,name..': discovery must wait for simulation')
    registered:update()
    assert(resumes==expectedResume,name..': resume count')
    assert(saves==expectedSave,name..': must not overwrite saved flags')
    if loadError or helpers=='error' then assert(registered.disabled,name..': fail closed')end
    count=count+1
end
local output=print
run('new match',{},false,0,1)
run('holder on restored match',{{valid=true,odf='mmm_holder'}},false,1,0)
run('mapper with extension',{{valid=true,odf='MMM_MAPPER.odf'}},false,1,0)
run('unreadable saved state',{{valid=true,odf='mmm_holder'}},true,1,0)
run('finder failure','error',false,0,0)
run('ordinary ship',{{valid=true,odf='fconst'}},false,0,1)
run('invalid old helper',{{valid=false,odf='mmm_holder'}},false,0,1)
print=output
print('Entry lifecycle: '..count..' passed')
