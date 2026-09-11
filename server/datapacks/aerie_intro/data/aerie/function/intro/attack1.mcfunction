execute as @a[scores={aerie_intro=1}] at @s run playsound minecraft:entity.generic.explode master @s ~ ~ ~ 1.5 0.8
execute as @a[scores={aerie_intro=1}] at @s run title @s times 5 30 10
execute as @a[scores={aerie_intro=1}] at @s run title @s title {"text":"— WE'RE HIT —","color":"red","bold":true}
execute as @a[scores={aerie_intro=1}] at @s run particle minecraft:explosion ~ ~2 ~ 5 2 2 2 0 force @s
execute as @a[scores={aerie_intro=1}] at @s run effect give @s minecraft:nausea 70 1 true
scoreboard players set @a[scores={aerie_intro=1}] aerie_shake 8
schedule function aerie:intro/shake_a 3
