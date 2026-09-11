execute as @a[scores={aerie_intro=1}] at @s run tp @s ~ ~ ~ ~-22 ~12
execute as @a[scores={aerie_intro=1}] at @s run playsound minecraft:entity.generic.explode master @s ~ ~ ~ 1.1 0.9
execute as @a[scores={aerie_intro=1}] at @s run particle minecraft:large_smoke ~ ~1 ~ 1 1 1 0.01 6 force @s
scoreboard players remove @a[scores={aerie_intro=1}] aerie_shake 1
execute if entity @a[scores={aerie_intro=1,aerie_shake=1..}] run schedule function aerie:intro/shake_a 3
execute if entity @a[scores={aerie_intro=1,aerie_shake=..0}] run schedule function aerie:intro/fall_start 20
