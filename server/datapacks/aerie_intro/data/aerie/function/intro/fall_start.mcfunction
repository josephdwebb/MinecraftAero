effect clear @s minecraft:nausea
title @s times 5 20 10
title @s title {"text":"— HULL BREACH —","color":"red","bold":true}
playsound minecraft:entity.generic.explode master @s ~ ~ ~ 2.0 0.6
playsound minecraft:entity.enderdragon.flap ambient @s ~ ~ ~ 1.0 0.5
gamemode spectator @s
scoreboard players set @s aerie_fall 180
schedule function aerie:intro/fall_tick 1
