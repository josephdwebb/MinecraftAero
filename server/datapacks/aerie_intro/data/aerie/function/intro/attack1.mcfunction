playsound minecraft:entity.generic.explode master @s ~ ~ ~ 1.5 0.8
title @s times 5 30 10
title @s title {"text":"— WE'RE HIT —","color":"red","bold":true}
particle minecraft:explosion ~ ~2 ~ 5 2 2 2 0 force @s
effect give @s minecraft:nausea 70 1 true
scoreboard players set @s aerie_shake 8
schedule function aerie:intro/shake_a 3
