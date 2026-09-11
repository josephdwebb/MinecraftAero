execute as @a[scores={aerie_intro=1}] at @s run title @s title {"text":"Nothing looks familiar.","color":"gray","italic":true}
execute as @a[scores={aerie_intro=1}] at @s run effect give @s minecraft:darkness 40 0 true
schedule function aerie:intro/wake3 80
