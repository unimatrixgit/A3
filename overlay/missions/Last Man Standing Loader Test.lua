class 'LastManStandingLoaderTest'

local function log(message)
    local text='Last Man Standing: '..tostring(message)
    print(text)
    if io and io.open then
        local file=io.open('LastManStanding-LoaderTest.log','a')
        if file then file:write(text..'\n');file:close() end
    end
end

function LastManStandingLoaderTest:__init()
    self.checked=false
end

function LastManStandingLoaderTest:setup()
    log('SETUP reached: native mission loader and Lua entry point work.')
    Objectives:load('LastManStandingLoaderTestObjectives.txt')
    Objectives.visible=true
end

function LastManStandingLoaderTest:update()
    if self.checked then return end
    self.checked=true
    local ok,err=pcall(function()
        log('UPDATE reached.')
        local entities=EntityFinder(function(e)
            return e.valid and e:isType(Entity.Type.Craft)
        end):find()
        log('Craft finder returned '..tostring(#entities)..' craft.')
        log('Player1 faction: '..Player(1).race.name)
        log('Player2 faction: '..Player(2).race.name)
        log('Player2 AI flag: '..tostring(Player(2).isAI))
        log('Map bounds: '..Map.min.x..','..Map.min.z..' to '..Map.max.x..','..Map.max.z)
        for _,entity in ipairs(entities) do
            if entity.valid and (entity:isType(Entity.Type.ConstructionRig)
                or entity:isType(Entity.Type.Starbase)) then
                local p=entity.position
                log('ANCHOR player='..entity.player.number..' odf='..entity.odf
                    ..' x='..p.x..' y='..p.y..' z='..p.z)
            end
        end
        log('SMOKE TEST PASSED. No ships/resources/rules modified by this script.')
    end)
    if not ok then log('SMOKE TEST FAILED: '..tostring(err)) end
end

MMM.register(LastManStandingLoaderTest())
