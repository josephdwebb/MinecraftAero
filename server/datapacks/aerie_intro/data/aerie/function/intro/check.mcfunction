scoreboard players add @a aerie_intro 0
execute as @a[scores={aerie_intro=0}] at @s run function aerie:intro/start
execute as @a[scores={aerie_intro=1}] at @s run function aerie:intro/tick
execute as @a[scores={aerie_skip=1..}] at @s run function aerie:intro/finish
