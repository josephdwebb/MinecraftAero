execute as @a[scores={aerie_intro=1}] at @s run tp @s ~ ~ ~ ~20 ~-10
execute as @a[scores={aerie_intro=1}] at @s run playsound minecraft:entity.generic.explode master @s ~ ~ ~ 1.3 1.0
execute as @a[scores={aerie_intro=1}] at @s run particle minecraft:large_smoke ~ ~1 ~ 1 1 1 0.01 6 force @s
scoreboard players remove @a[scores={aerie_intro=1}] aerie_shake 1
execute if entity @a[scores={aerie_intro=1,aerie_shake=1..}] run schedule function aerie:intro/shake_b 3
execute if entity @a[scores={aerie_intro=1,aerie_shake=..0}] run schedule function aerie:intro/fall_start 20
