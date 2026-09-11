# Objectives
scoreboard objectives add aerie_intro dummy
scoreboard objectives add aerie_t dummy
scoreboard objectives add aerie_mode dummy
scoreboard objectives add aerie_cam dummy
scoreboard objectives add aerie_skip trigger

# Camera path constants (centi-blocks; position is a pure function of aerie_t)
# start t=220 -> (-109.4, 110.8, -156.0)   end t=0 -> (-72.0, 80.0, -112.0)
scoreboard players set #k17 aerie_cam 17
scoreboard players set #k14 aerie_cam 14
scoreboard players set #k20 aerie_cam 20
scoreboard players set #neg aerie_cam -1
scoreboard players set #bx aerie_cam -7200
scoreboard players set #by aerie_cam 8000
scoreboard players set #bz aerie_cam -11200

# Purge any legacy scheduled steps from earlier implementations
schedule clear aerie:intro/title1
schedule clear aerie:intro/title2
schedule clear aerie:intro/attack1
schedule clear aerie:intro/shake_a
schedule clear aerie:intro/shake_b
schedule clear aerie:intro/fall_start
schedule clear aerie:intro/fall_tick
schedule clear aerie:intro/blackout
schedule clear aerie:intro/wake1
schedule clear aerie:intro/wake2
schedule clear aerie:intro/wake3
schedule clear aerie:intro/wake4

# Anyone caught mid-scene by a reload gets released
execute as @a[scores={aerie_intro=1}] at @s run function aerie:intro/finish
