scoreboard objectives add aerie_intro dummy
scoreboard objectives add aerie_t dummy
scoreboard objectives add aerie_mode dummy
scoreboard objectives add aerie_cam dummy
scoreboard objectives add aerie_skip trigger

# Camera path, centi-blocks, as a pure function of aerie_t (220 -> 0):
#   x = -5900 - t*5    (-70.00 -> -59.00)
#   y = 12800 + t*19   (170.00 -> 128.00)
#   z = -3800 + t*25   ( 17.00 ->  -38.00)
# Fixed rotation yaw -164 / pitch 42 keeps the hub framed the whole way.
scoreboard players set #kx aerie_cam 5
scoreboard players set #ky aerie_cam 19
scoreboard players set #kz aerie_cam 25
scoreboard players set #neg aerie_cam -1
scoreboard players set #bx aerie_cam -5900
scoreboard players set #by aerie_cam 12800
scoreboard players set #bz aerie_cam -3800

# Release anyone caught mid-scene by a reload, and clear orphaned cameras
execute as @a[scores={aerie_intro=1}] at @s run function aerie:intro/finish
kill @e[type=minecraft:text_display,tag=aerie_cam_e]
