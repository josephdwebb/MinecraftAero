# Release the player. Safe to run manually for recovery:
#   /execute as PLAYER run function aerie:intro/finish
scoreboard players set @s aerie_intro 3
scoreboard players set @s aerie_t 0
scoreboard players reset @s aerie_skip
title @s clear
title @s times 10 60 20
effect clear @s minecraft:blindness
effect clear @s minecraft:darkness
stopsound @s ambient
gamemode survival @s
execute if score @s aerie_mode matches 1 run gamemode creative @s
execute if score @s aerie_mode matches 2 run gamemode adventure @s
execute if score @s aerie_mode matches 3 run gamemode spectator @s
tp @s -70 76 -108 facing -46 80 -64
title @s actionbar {"text":"Get your bearings \u2014 open your quest book","color":"yellow"}
