execute as @a[scores={aerie_intro=1}] at @s run effect give @s minecraft:blindness 200 255 true
execute as @a[scores={aerie_intro=1}] at @s run effect give @s minecraft:darkness 200 0 true
execute as @a[scores={aerie_intro=1}] at @s run playsound minecraft:entity.player.big_fall ambient @s ~ ~ ~ 1.5 0.7
execute as @a[scores={aerie_intro=1}] at @s run playsound minecraft:entity.generic.hurt master @s ~ ~ ~ 1.0 0.5
gamemode survival @a[scores={aerie_intro=1}]
tp @a[scores={aerie_intro=1}] -70 76 -108 0 0
execute as @a[scores={aerie_intro=1}] at @s run title @s times 60 100 40
execute as @a[scores={aerie_intro=1}] at @s run title @s title {"text":"...","color":"dark_gray"}
schedule function aerie:intro/wake1 70
