tp @s ~ ~ ~ ~20 ~-10
playsound minecraft:entity.generic.explode master @s ~ ~ ~ 1.3 1.0
particle minecraft:large_smoke ~ ~1 ~ 1 1 1 0.01 6 force @s
scoreboard players remove @s aerie_shake 1
execute if score @s aerie_shake matches 1.. run schedule function aerie:intro/shake_b 3
execute if score @s aerie_shake matches ..0 run schedule function aerie:intro/fall_start 20
