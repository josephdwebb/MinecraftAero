execute as @a[scores={aerie_intro=1}] at @s run effect clear @s minecraft:nausea
execute as @a[scores={aerie_intro=1}] at @s run title @s times 5 20 10
execute as @a[scores={aerie_intro=1}] at @s run title @s title {"text":"— HULL BREACH —","color":"red","bold":true}
execute as @a[scores={aerie_intro=1}] at @s run playsound minecraft:entity.generic.explode master @s ~ ~ ~ 2.0 0.6
execute as @a[scores={aerie_intro=1}] at @s run playsound minecraft:entity.enderdragon.flap ambient @s ~ ~ ~ 1.0 0.5
gamemode spectator @a[scores={aerie_intro=1}]
scoreboard players set @a[scores={aerie_intro=1}] aerie_fall 180
schedule function aerie:intro/fall_tick 1
