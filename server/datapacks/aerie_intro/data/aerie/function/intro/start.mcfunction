# Runs as the joining player, with @s bound.
scoreboard players set @s aerie_intro 1
scoreboard players set @s aerie_t 220

scoreboard players set @s aerie_mode 0
execute if entity @s[gamemode=creative] run scoreboard players set @s aerie_mode 1
execute if entity @s[gamemode=adventure] run scoreboard players set @s aerie_mode 2
execute if entity @s[gamemode=spectator] run scoreboard players set @s aerie_mode 3

scoreboard players set @s aerie_skip 0
scoreboard players enable @s aerie_skip

gamemode spectator @s
title @s clear
title @s times 40 120 30

# Move the body to the camera start so those chunks are loaded, then hand the
# view to a camera entity. Spectating an entity ignores mouse input entirely,
# so the player cannot fight the camera.
execute in minecraft:overworld run tp @s -70.0 170.0 17.0 -164 42
kill @e[type=minecraft:item_display,tag=aerie_cam_e]
execute in minecraft:overworld run summon minecraft:item_display -70.0 170.0 17.0 {Tags:["aerie_cam_e"],teleport_duration:3,Rotation:[-164f,42f]}
spectate @e[type=minecraft:item_display,tag=aerie_cam_e,limit=1] @s

effect give @s minecraft:blindness 2 0 true
stopsound @s
execute at @s run playsound aerie:theme record @s ~ ~ ~ 1 1 1
tellraw @s [{"text":"Skip arrival: ","color":"dark_gray"},{"text":"/trigger aerie_skip","color":"gray","clickEvent":{"action":"run_command","value":"/trigger aerie_skip"}}]
