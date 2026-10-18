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
                    if committed == "indeterminate" then
                        -- A partial engine rollback could not be verified: never duplicate a fleet.
                        results[#results+1] = { player=team.number, status="deployment_needs_review" }
                    elseif not ok or not committed then
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
