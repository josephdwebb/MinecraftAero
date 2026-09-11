effect clear @s minecraft:blindness
effect clear @s minecraft:darkness
title @s times 10 40 15
title @s title {"text":"Get your bearings.","color":"white"}
title @s subtitle {"text":"Start with the basics.","color":"yellow"}
playsound aerie:theme record @s ~ ~ ~ 0.5 1.0
scoreboard players set @s aerie_intro 3
