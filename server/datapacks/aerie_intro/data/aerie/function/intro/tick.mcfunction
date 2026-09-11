scoreboard players remove @s aerie_t 1

scoreboard players operation #cx aerie_cam = @s aerie_t
scoreboard players operation #cx aerie_cam *= #kx aerie_cam
scoreboard players operation #cx aerie_cam *= #neg aerie_cam
scoreboard players operation #cx aerie_cam += #bx aerie_cam

scoreboard players operation #cy aerie_cam = @s aerie_t
scoreboard players operation #cy aerie_cam *= #ky aerie_cam
scoreboard players operation #cy aerie_cam += #by aerie_cam

scoreboard players operation #cz aerie_cam = @s aerie_t
scoreboard players operation #cz aerie_cam *= #kz aerie_cam
scoreboard players operation #cz aerie_cam += #bz aerie_cam

execute store result storage aerie:cam x double 0.01 run scoreboard players get #cx aerie_cam
execute store result storage aerie:cam y double 0.01 run scoreboard players get #cy aerie_cam
execute store result storage aerie:cam z double 0.01 run scoreboard players get #cz aerie_cam
function aerie:intro/move with storage aerie:cam

execute if score @s aerie_t matches 190 run title @s title {"text":"Outlands of Aerie","color":"gold","bold":true}
execute if score @s aerie_t matches 190 run title @s subtitle {"text":"Nowhere to go but up","color":"gray","italic":true}
execute if score @s aerie_t matches 20 run effect give @s minecraft:blindness 4 0 true
execute if score @s aerie_t matches ..0 run function aerie:intro/finish
