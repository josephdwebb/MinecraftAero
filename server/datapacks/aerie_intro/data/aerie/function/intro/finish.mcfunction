# Release the player. Safe to run manually:
#   /execute as PLAYER run function aerie:intro/finish
scoreboard players set @s aerie_intro 3
scoreboard players set @s aerie_t 0
scoreboard players reset @s aerie_skip
spectate
kill @e[type=minecraft:item_display,tag=aerie_cam_e]
title @s clear
title @s times 10 60 20
gamemode survival @s
execute if score @s aerie_mode matches 1 run gamemode creative @s
execute if score @s aerie_mode matches 2 run gamemode adventure @s
execute if score @s aerie_mode matches 3 run gamemode spectator @s
execute in minecraft:overworld run tp @s -70 76 -108 facing -46 80 -64
effect clear @s minecraft:blindness
effect clear @s minecraft:darkness
