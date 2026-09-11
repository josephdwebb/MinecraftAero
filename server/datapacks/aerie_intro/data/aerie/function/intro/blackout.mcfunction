effect give @s minecraft:blindness 200 255 true
effect give @s minecraft:darkness 200 0 true
playsound minecraft:entity.player.big_fall ambient @s ~ ~ ~ 1.5 0.7
playsound minecraft:entity.generic.hurt master @s ~ ~ ~ 1.0 0.5
gamemode survival @s
tp @s -70 76 -108 0 0
title @s times 60 100 40
title @s title {"text":"...","color":"dark_gray"}
schedule function aerie:intro/wake1 70
