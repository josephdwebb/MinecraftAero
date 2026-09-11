scoreboard players set @s aerie_intro 1
gamemode adventure @s
effect give @s minecraft:blindness 30 255 true
tp @s -68 285 -132 0 0
title @s times 40 60 40
playsound aerie:theme record @s -68 285 -132 1.0 1.0
schedule function aerie:intro/title1 60
