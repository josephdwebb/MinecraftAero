# Runs as the player, once per tick, while aerie_intro=1.
scoreboard players remove @s aerie_t 1

# Camera position is a pure function of aerie_t (no accumulation, no drift,
# safe for two players running the scene at once).
scoreboard players operation #cx aerie_cam = @s aerie_t
scoreboard players operation #cx aerie_cam *= #k17 aerie_cam
scoreboard players operation #cx aerie_cam *= #neg aerie_cam
scoreboard players operation #cx aerie_cam += #bx aerie_cam

scoreboard players operation #cy aerie_cam = @s aerie_t
scoreboard players operation #cy aerie_cam *= #k14 aerie_cam
scoreboard players operation #cy aerie_cam += #by aerie_cam

scoreboard players operation #cz aerie_cam = @s aerie_t
scoreboard players operation #cz aerie_cam *= #k20 aerie_cam
scoreboard players operation #cz aerie_cam *= #neg aerie_cam
scoreboard players operation #cz aerie_cam += #bz aerie_cam

execute store result storage aerie:cam x double 0.01 run scoreboard players get #cx aerie_cam
execute store result storage aerie:cam y double 0.01 run scoreboard players get #cy aerie_cam
execute store result storage aerie:cam z double 0.01 run scoreboard players get #cz aerie_cam
function aerie:intro/move with storage aerie:cam

# Beats
execute if score @s aerie_t matches 180 run title @s title {"text":"Outlands of Aerie","color":"gold","bold":true}
execute if score @s aerie_t matches 180 run title @s subtitle {"text":"Nowhere to go but up","color":"gray","italic":true}
execute if score @s aerie_t matches 110 at @s run playsound minecraft:ambient.basalt_deltas.loop ambient @s ~ ~ ~ 0.4 0.85
execute if score @s aerie_t matches ..0 run function aerie:intro/finish
