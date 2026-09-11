scoreboard players remove @s aerie_fall 1
tp @s ~ ~-1.1 ~ ~1 ~
execute if score @s aerie_fall matches 120 run playsound minecraft:entity.enderdragon.flap ambient @s ~ ~ ~ 0.8 0.6
execute if score @s aerie_fall matches 60 run playsound minecraft:entity.enderdragon.flap ambient @s ~ ~ ~ 0.8 0.7
execute if score @s aerie_fall matches 1.. run schedule function aerie:intro/fall_tick 1
execute if score @s aerie_fall matches ..0 run schedule function aerie:intro/blackout 5
