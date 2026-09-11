scoreboard players remove @a[scores={aerie_intro=1}] aerie_fall 1
execute as @a[scores={aerie_intro=1}] at @s run tp @s ~ ~-1.1 ~ ~1 ~
execute as @a[scores={aerie_intro=1,aerie_fall=120}] at @s run playsound minecraft:entity.enderdragon.flap ambient @s ~ ~ ~ 0.8 0.6
execute as @a[scores={aerie_intro=1,aerie_fall=60}] at @s run playsound minecraft:entity.enderdragon.flap ambient @s ~ ~ ~ 0.8 0.7
execute if entity @a[scores={aerie_intro=1,aerie_fall=1..}] run schedule function aerie:intro/fall_tick 1
execute if entity @a[scores={aerie_intro=1,aerie_fall=..0}] run schedule function aerie:intro/blackout 5
