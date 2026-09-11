execute as @a[scores={aerie_intro=1}] at @s run effect clear @s minecraft:blindness
execute as @a[scores={aerie_intro=1}] at @s run effect clear @s minecraft:darkness
execute as @a[scores={aerie_intro=1}] at @s run title @s times 10 40 15
execute as @a[scores={aerie_intro=1}] at @s run title @s title {"text":"Get your bearings.","color":"white"}
execute as @a[scores={aerie_intro=1}] at @s run title @s subtitle {"text":"Start with the basics.","color":"yellow"}
execute as @a[scores={aerie_intro=1}] at @s run playsound aerie:theme record @s ~ ~ ~ 0.5 1.0
scoreboard players set @a[scores={aerie_intro=1}] aerie_intro 3
