import turtle
import math

# ============================================================
# Bangladesh National Parliament Building - Turtle Drawing
# Stylized approximation based on the reference image.
#
# Controls:
#   Esc / Q -> close
#   S       -> save as EPS
#   D       -> day mode
#   N       -> night mode
#   Space   -> toggle day/night
# ============================================================

screen = turtle.Screen()
screen.title("Bangladesh National Parliament Building - Turtle Art")
screen.setup(width=1.0, height=1.0)
screen.bgcolor("#86d0f2")
screen.tracer(0, 0)

W = screen.window_width()
H = screen.window_height()

# Logical drawing area: 1280 x 720
SX = W / 1280
SY = H / 720

pen = turtle.Turtle(visible=False)
pen.speed(0)
pen.penup()
pen.pensize(2)

def pt(x, y):
    """Convert image-style coordinates (origin top-left) to Turtle coordinates."""
    return (x * SX - W / 2, H / 2 - y * SY)

def goto(x, y):
    pen.goto(*pt(x, y))

def polygon(points, fill, outline="#202020", width=2):
    pen.penup()
    goto(*points[0])
    pen.pendown()
    pen.pensize(width)
    pen.color(outline, fill)
    pen.begin_fill()
    for x, y in points[1:]:
        goto(x, y)
    goto(*points[0])
    pen.end_fill()
    pen.penup()

def line(points, color="#202020", width=2):
    pen.penup()
    goto(*points[0])
    pen.pendown()
    pen.pensize(width)
    pen.pencolor(color)
    for x, y in points[1:]:
        goto(x, y)
    pen.penup()

def rect(x1, y1, x2, y2, fill, outline="#202020", width=2):
    polygon([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], fill, outline, width)

def ellipse(cx, cy, rx, ry, fill, outline="#202020", width=2, steps=80):
    pts = []
    for i in range(steps):
        a = 2 * math.pi * i / steps
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    polygon(pts, fill, outline, width)

def arc_shape(cx, cy, rx, ry, start_deg, end_deg, fill=None,
              outline="#202020", width=2, steps=50):
    pts = []
    for i in range(steps + 1):
        a = math.radians(start_deg + (end_deg-start_deg)*i/steps)
        pts.append((cx + rx*math.cos(a), cy + ry*math.sin(a)))
    if fill:
        pts.append((cx, cy))
        polygon(pts, fill, outline, width)
    else:
        line(pts, outline, width)

def cloud(x, y, scale=1.0):
    color = "#f7f7f7"
    ellipse(x, y, 60*scale, 28*scale, color, color, 1)
    ellipse(x+45*scale, y-18*scale, 48*scale, 38*scale, color, color, 1)
    ellipse(x+95*scale, y, 65*scale, 31*scale, color, color, 1)
    polygon([(x-60*scale,y+8*scale),(x+160*scale,y+8*scale),
             (x+140*scale,y+27*scale),(x-85*scale,y+27*scale)],
            color, color, 1)

def draw_flag_pole(x, top_y, floor_y, width=3):
    """Draw a flag stand from the flag position down to the floor."""
    line([(x, top_y), (x, floor_y)], "#2d2d2d", width)
    ellipse(x, top_y, 3, 3, "#b8b8a8", "#202020", 1)

def make_flag_turtle():
    t = turtle.Turtle(visible=False)
    t.speed(0)
    t.penup()
    return t

def draw_waving_flag(t, x, y, scale, phase):
    """Draw an animated Bangladesh flag moving in the wind."""
    t.clear()
    anchor_x, anchor_y = pt(x, y)

    wave1 = math.sin(phase) * 5 * scale
    wave2 = math.sin(phase + 1.3) * 7 * scale
    wave3 = math.sin(phase + 2.2) * 5 * scale

    cloth = [
        (0, 0),
        (24*scale, 5*scale + wave1),
        (50*scale, 1*scale + wave2),
        (76*scale, 5*scale + wave3),
        (73*scale, -34*scale + wave3),
        (48*scale, -29*scale + wave2),
        (24*scale, -35*scale + wave1),
        (0, -39*scale),
    ]

    t.goto(anchor_x, anchor_y)
    t.pensize(max(1, int(2*scale)))
    t.color("#173b2a", "#087b39")
    t.begin_fill()
    t.pendown()
    for px, py in cloth:
        t.goto(anchor_x + px*SX, anchor_y + py*SY)
    t.goto(anchor_x, anchor_y)
    t.end_fill()
    t.penup()

    # Red circle follows the cloth movement.
    disc_x = anchor_x + 47*scale*SX
    disc_y = anchor_y + (-18*scale + wave2*0.45)*SY
    radius = 12*scale*min(SX, SY)
    t.goto(disc_x, disc_y - radius)
    t.setheading(0)
    t.color("#9f101a", "#e7202c")
    t.begin_fill()
    t.pendown()
    t.circle(radius)
    t.end_fill()
    t.penup()

def make_animation_turtle():
    t = turtle.Turtle(visible=False)
    t.speed(0)
    t.penup()
    return t

def logical_goto(t, x, y):
    t.goto(*pt(x, y))

def draw_moving_cloud(t, x, y, scale, night=False):
    """Draw a moving cloud. Night clouds use layered blurry ash colours."""
    t.clear()
    t.penup()

    if night:
        # Layered grey dots create a soft/blurry ash-cloud appearance.
        layers = [
            ("#5e6570", 1.14, 5),
            ("#747b85", 1.06, 3),
            ("#8b919a", 0.97, 0),
        ]
    else:
        layers = [
            ("#eef7fb", 1.07, 3),
            ("#ffffff", 1.00, 0),
        ]

    pieces = [
        (-42, 7, 45), (0, -10, 62), (48, 2, 52),
        (88, 10, 42), (22, 13, 76)
    ]

    for colour, layer_scale, offset in layers:
        for dx, dy, diameter in pieces:
            logical_goto(
                t,
                x + (dx + offset) * scale,
                y + (dy + offset * 0.12) * scale
            )
            t.dot(
                max(3, int(diameter * scale * layer_scale * min(SX, SY))),
                colour
            )

def draw_bird(t, x, y, scale, wing_phase):
    """Draw one flying bird using two animated curved wings."""
    t.clear()
    t.penup()
    t.pencolor("#252525")
    t.pensize(max(1, int(2.2 * scale)))

    flap = math.sin(wing_phase) * 7 * scale
    px, py = pt(x, y)

    # Left wing
    t.goto(px - 18*scale*SX, py + flap*SY)
    t.pendown()
    t.goto(px, py - 5*scale*SY)
    t.penup()

    # Right wing
    t.goto(px, py - 5*scale*SY)
    t.pendown()
    t.goto(px + 18*scale*SX, py + flap*SY)
    t.penup()

def draw_night_lights(t, phase):
    """Draw small glowing lights around the Parliament building."""
    t.clear()
    if not night_mode:
        return

    light_points = [
        (390, 214, 7), (455, 203, 6), (550, 198, 6),
        (670, 198, 6), (760, 204, 6), (845, 218, 7),
        (309, 465, 9), (927, 465, 9),
        (73, 518, 6), (239, 518, 6), (1008, 518, 6), (1185, 518, 6),
        (594, 500, 6), (630, 500, 6),
        (430, 569, 5), (570, 569, 5), (690, 569, 5), (810, 569, 5),
        (365, 554, 5), (850, 548, 5), (970, 544, 5),
    ]

    glow = 0.78 + 0.22 * math.sin(phase)
    core_colour = "#fff3a6" if glow > 0.82 else "#ffe477"

    for x, y, size in light_points:
        logical_goto(t, x, y)
        t.dot(int(size * 2.4 * min(SX, SY)), "#9c7b35")
        logical_goto(t, x, y)
        t.dot(int(size * 1.35 * min(SX, SY)), core_colour)

def set_day_mode():
    global night_mode
    night_mode = False
    screen.bgcolor("#86d0f2")

def set_night_mode():
    global night_mode
    night_mode = True
    screen.bgcolor("#101a35")

def toggle_day_night():
    if night_mode:
        set_day_mode()
    else:
        set_night_mode()

# ---------------------- SKY ----------------------
# The sky uses screen.bgcolor so it can change between day and night.
screen.bgcolor("#86d0f2")

# ---------------------- DISTANT GROUND ----------------------
rect(0, 570, 1280, 720, "#853e38", "#2b211f", 2)

# ---------------------- MAIN BUILDING ----------------------
sand = "#d7bc82"
sand_light = "#e1c995"
shadow = "#887d6c"
dark = "#4e4a45"
glass = "#4ea5d2"
glass_dark = "#28769e"
brick = "#9a7c57"

# Side wings
polygon([(0,330),(25,330),(25,306),(145,288),(145,305),(260,270),
         (360,270),(360,585),(0,585)], sand, "#202020", 2)
polygon([(920,275),(1010,270),(1120,295),(1210,310),(1210,330),
         (1280,330),(1280,585),(920,585)], sand, "#202020", 2)

# Mid side masses
polygon([(130,306),(260,270),(455,270),(455,585),(130,585)],
        sand_light, "#202020", 2)
polygon([(825,275),(1010,270),(1160,305),(1160,585),(825,585)],
        sand_light, "#202020", 2)

# Central upper crown
polygon([(345,200),(370,187),(520,170),(705,170),(860,195),
         (890,214),(890,305),(345,305)], sand_light, "#202020", 2)

# Upper tower blocks
polygon([(305,210),(345,200),(345,305),(305,305)], shadow, "#202020", 2)
polygon([(890,214),(920,208),(930,305),(890,305)], shadow, "#202020", 2)

# Crown vertical divisions
for x in [405, 520, 705, 780]:
    polygon([(x,180),(x+18,176),(x+18,275),(x,286)],
            sand, "#202020", 2)

# Crown arches/windows
arc_shape(398, 225, 31, 31, 180, 360, dark, "#202020", 2)
rect(368,225,428,270,dark,"#202020",2)
rect(378,235,418,271,glass,"#202020",2)

arc_shape(835, 226, 31, 31, 180, 360, dark, "#202020", 2)
rect(805,226,865,270,dark,"#202020",2)
rect(815,236,855,271,glass,"#202020",2)

# Central crown glass band
rect(535,215,700,258,glass_dark,"#202020",2)
for x in range(555, 700, 35):
    line([(x,215),(x,258)], "#202020", 1)
line([(535,238),(700,238)], "#202020", 1)

# Central cylindrical masses
polygon([(370,255),(430,242),(550,242),(585,255),(585,585),
         (365,585)], sand_light, "#202020", 2)
polygon([(585,255),(620,242),(750,242),(800,260),(800,585),
         (585,585)], sand, "#202020", 2)

# Deep central notch
polygon([(565,260),(585,255),(585,480),(620,480),(620,260),
         (640,250),(640,585),(565,585)], "#655d53", "#202020", 2)

# Main entrance glazing
rect(585,485,640,585,glass_dark,"#202020",2)
line([(612,485),(612,585)], "#202020", 2)
line([(585,530),(640,530)], "#202020", 2)

# Cylindrical highlights / horizontal layers
for y in range(285, 560, 18):
    line([(373,y),(582,y)], "#ead9b4", 1)
    line([(642,y),(798,y)], "#ead9b4", 1)

# Side wall vertical separators
for x in [145, 265, 350, 455, 825, 920, 1010, 1120, 1210]:
    line([(x,290),(x,585)], "#675e51", 2)

# Side wall horizontal masonry lines
for y in range(335, 570, 18):
    line([(0,y),(365,y)], "#ead9b4", 1)
    line([(800,y),(1280,y)], "#ead9b4", 1)

# Triangular windows
def triangular_window(x, top_y, base_y, half_width):
    polygon([(x,top_y),(x-half_width,base_y),(x+half_width,base_y)],
            dark, "#202020", 2)
    polygon([(x,top_y+45),(x-half_width*0.42,base_y-10),
             (x+half_width*0.42,base_y-10)],
            glass, "#202020", 1)
    line([(x,top_y+45),(x,base_y-10)], "#202020", 1)

triangular_window(52,320,468,24)
triangular_window(234,292,454,29)
triangular_window(1001,302,454,31)
triangular_window(1183,328,468,24)

# Circular windows
ellipse(308, 465, 38, 38, dark, "#202020", 2)
ellipse(308, 465, 29, 31, glass, "#202020", 2)
ellipse(927, 465, 38, 38, dark, "#202020", 2)
ellipse(927, 465, 29, 31, glass, "#202020", 2)
line([(910,485),(943,445)], "#b8e6fa", 5)

# Rectangular windows and doors
for x in [52, 218, 987, 1165]:
    rect(x,500,x+42,585,glass_dark,"#202020",2)
    line([(x+21,500),(x+21,585)], "#202020", 1)
    for yy in [526,552]:
        line([(x,yy),(x+42,yy)], "#202020", 1)

# Add building shadows
polygon([(445,220),(515,220),(610,325),(610,480),(530,380)],
        "#8d8270", "#8d8270", 1)
polygon([(750,250),(800,260),(800,460),(720,350)],
        "#958976", "#958976", 1)
polygon([(1060,285),(1120,295),(1195,390),(1195,475)],
        "#968a78", "#968a78", 1)

# Vertical flag poles on roof
for x, top in [(435,102),(615,46),(940,0)]:
    line([(x,top),(x,190 if x!=940 else 275)], "#282828", 3)

# ---------------------- FLAG STANDS ----------------------
# Each stand reaches the building floor at y = 585.
flag_specs = [
    (615, 55, 1.00, 585),
    (195, 505, 0.45, 585),
    (278, 500, 0.48, 585),
    (345, 493, 0.55, 585),
    (620, 498, 0.55, 585),
    (931, 504, 0.52, 585),
]

for fx, fy, fs, floor_y in flag_specs:
    draw_flag_pole(fx, fy, floor_y, 3 if fs >= 0.9 else 2)
# ---------------------- STAIRS ----------------------
# Main stair block
polygon([(155,585),(1120,585),(1275,720),(0,720)],
        "#7f3935", "#2b211f", 2)

# Side ramps
polygon([(0,585),(345,585),(205,720),(0,720)],
        "#8b3d38", "#2b211f", 2)
polygon([(880,585),(1280,585),(1280,720),(1035,720)],
        "#8b3d38", "#2b211f", 2)

# Stair treads
for y in range(592, 720, 11):
    t = (y - 585) / 135
    left = 145 - 145*t
    right = 1125 + 155*t
    line([(left,y),(right,y)], "#2f2422", 2)

# Ramp borders
line([(0,635),(345,585)], "#d6c3b4", 6)
line([(90,720),(345,585)], "#d6c3b4", 6)
line([(880,585),(1035,720)], "#d6c3b4", 6)
line([(880,585),(1280,675)], "#d6c3b4", 6)

# Handrails
for x in [430, 570, 690, 810]:
    line([(x,570),(x,720)], "#272727", 3)
    ellipse(x,570,4,4,"#bbb49b","#272727",1)

# Side railings
for x1, y1, x2, y2 in [(350,555,350,605),(570,555,570,610),
                       (690,555,690,610),(850,545,850,600),
                       (970,540,970,600)]:
    line([(x1,y1),(x2,y2)], "#333333", 3)

# Front edge
line([(0,718),(1280,718)], "#221b1a", 4)

# Save helper
def save_eps():
    screen.getcanvas().postscript(file="parliament_building.eps")
    print("Saved as parliament_building.eps")

screen.listen()
screen.onkey(screen.bye, "Escape")
screen.onkey(screen.bye, "q")
screen.onkey(screen.bye, "Q")
screen.onkey(save_eps, "s")
screen.onkey(save_eps, "S")
screen.onkey(set_day_mode, "d")
screen.onkey(set_day_mode, "D")
screen.onkey(set_night_mode, "n")
screen.onkey(set_night_mode, "N")
screen.onkey(toggle_day_night, "space")

# ---------------------- COMPLETE ANIMATION ----------------------
animated_flags = [make_flag_turtle() for _ in flag_specs]

cloud_turtles = [make_animation_turtle() for _ in range(4)]
cloud_data = [
    [-90.0, 78.0, 0.78, 0.72],
    [290.0, 105.0, 0.58, 0.48],
    [790.0, 72.0, 0.72, 0.62],
    [1130.0, 118.0, 0.52, 0.42],
]

bird_turtles = [make_animation_turtle() for _ in range(7)]
bird_data = [
    [-80.0, 150.0, 0.72, 1.55],
    [120.0, 205.0, 0.55, 1.25],
    [360.0, 125.0, 0.62, 1.45],
    [590.0, 170.0, 0.48, 1.18],
    [820.0, 130.0, 0.68, 1.50],
    [1030.0, 195.0, 0.52, 1.28],
    [1210.0, 145.0, 0.60, 1.40],
]

light_turtle = make_animation_turtle()

animation_phase = 0.0
night_mode = False

def animate_scene():
    global animation_phase
    animation_phase += 0.14

    # Flags wave in both day and night.
    for index, ((fx, fy, fs, _), flag_turtle) in enumerate(
            zip(flag_specs, animated_flags)):
        draw_waving_flag(
            flag_turtle, fx, fy, fs,
            animation_phase + index * 0.65
        )

    # Clouds continuously move from left to right.
    for index, (cloud_turtle, data) in enumerate(zip(cloud_turtles, cloud_data)):
        data[0] += data[3]
        cloud_width = 210 * data[2]
        if data[0] - cloud_width > 1280:
            data[0] = -cloud_width
            data[1] = 55 + (index * 43) % 105

        draw_moving_cloud(
            cloud_turtle,
            data[0],
            data[1],
            data[2],
            night=night_mode
        )

    # Birds fly only during day mode.
    for index, (bird_turtle, data) in enumerate(zip(bird_turtles, bird_data)):
        if night_mode:
            bird_turtle.clear()
            continue

        data[0] += data[3]
        if data[0] > 1320:
            data[0] = -70
            data[1] = 105 + (index * 31) % 125

        draw_bird(
            bird_turtle,
            data[0],
            data[1] + math.sin(animation_phase + index) * 5,
            data[2],
            animation_phase * 2.5 + index
        )

    # Small lights appear around the building only at night.
    draw_night_lights(light_turtle, animation_phase * 1.8)

    screen.update()
    screen.ontimer(animate_scene, 35)

animate_scene()
turtle.done()