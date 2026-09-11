# Runs as the joining player, with @s bound.
scoreboard players set @s aerie_intro 1
scoreboard players set @s aerie_t 220

# Remember gamemode so testing from creative doesn't strand you in survival
scoreboard players set @s aerie_mode 0
execute if entity @s[gamemode=creative] run scoreboard players set @s aerie_mode 1
execute if entity @s[gamemode=adventure] run scoreboard players set @s aerie_mode 2
execute if entity @s[gamemode=spectator] run scoreboard players set @s aerie_mode 3

scoreboard players set @s aerie_skip 0
scoreboard players enable @s aerie_skip

gamemode spectator @s
title @s clear
title @s times 40 100 40
effect give @s minecraft:blindness 2 0 true
execute at @s run playsound minecraft:ambient.basalt_deltas.loop ambient @s ~ ~ ~ 0.5 0.8
tellraw @s [{"text":"Skip arrival: ","color":"dark_gray"},{"text":"/trigger aerie_skip","color":"gray","clickEvent":{"action":"run_command","value":"/trigger aerie_skip"}}]
