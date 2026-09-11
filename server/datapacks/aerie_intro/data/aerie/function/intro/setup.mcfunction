scoreboard objectives add aerie_intro dummy
scoreboard objectives add aerie_shake dummy
scoreboard objectives add aerie_fall dummy
scoreboard objectives add aerie_global dummy
execute unless score #global aerie_global matches 1 run function aerie:intro/place_airship
