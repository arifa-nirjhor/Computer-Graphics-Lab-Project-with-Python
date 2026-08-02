"""
Project: Interactive Bangladesh Victory Day Graphics Simulator
Language: Python
Library: turtle

Controls:
    D  -> Day mode
    N  -> Night mode
    P  -> Pause/resume animation
    Left/Right arrows -> Move car manually
    Up/Down arrows -> Increase/decrease car speed
    R  -> Reset the scene
    F  -> Show/hide fireworks
    Esc -> Close program
"""

import turtle
import math
import random

# -----------------------------
# SCREEN CONFIGURATION
# -----------------------------
WIDTH = 1000
HEIGHT = 700

screen = turtle.Screen()

# Use the complete monitor area.
screen.setup(width=1.0, height=1.0)
root = screen.getcanvas().winfo_toplevel()
root.attributes("-fullscreen", True)
root.update_idletasks()

# Stretch the complete 1000 x 700 drawing coordinate area
# across the full-screen Turtle canvas.
screen.setworldcoordinates(-500, -350, 500, 350)

screen.title("Interactive Bangladesh Victory Day Graphics Simulator")
screen.bgcolor("#87CEEB")
screen.tracer(0)

# -----------------------------
# GLOBAL STATE
# -----------------------------
is_night = False
paused = False
show_fireworks = True

car_x = -520
car_speed = 3

cloud_x = -500
bird_x = -450
wheel_angle = 0
wave_time = 0.0
firework_radius = 5

upper_car_x = -650
lower_car_x = 650

car_motion_speed = 2.6
car_moving = True

cloud_speed = 1.2
cloud_moving = True

bird_speed = 1.8
birds_moving = True

# -----------------------------
# TURTLE OBJECTS
# -----------------------------
static_pen = turtle.Turtle(visible=False)
static_pen.speed(0)
static_pen.penup()

algorithm_pen = turtle.Turtle(visible=False)
algorithm_pen.speed(0)
algorithm_pen.penup()

dynamic_pen = turtle.Turtle(visible=False)
dynamic_pen.speed(0)
dynamic_pen.penup()

text_pen = turtle.Turtle(visible=False)
text_pen.speed(0)
text_pen.penup()


# -----------------------------
# BASIC DRAWING HELPERS
# -----------------------------
def jump(pen, x, y):
    pen.penup()
    pen.goto(x, y)
    pen.pendown()


def filled_rectangle(pen, x, y, width, height, color):
    """Draw rectangle from bottom-left coordinate."""
    jump(pen, x, y)
    pen.setheading(0)
    pen.color(color)
    pen.fillcolor(color)
    pen.begin_fill()

    for length in (width, height, width, height):
        pen.forward(length)
        pen.left(90)

    pen.end_fill()
    pen.penup()


def filled_polygon(pen, points, color):
    if not points:
        return

    pen.penup()
    pen.goto(points[0])
    pen.color(color)
    pen.fillcolor(color)
    pen.begin_fill()
    pen.pendown()

    for point in points[1:]:
        pen.goto(point)

    pen.goto(points[0])
    pen.end_fill()
    pen.penup()


def filled_circle(pen, x, y, radius, color):
    """Draw a filled circle where (x, y) is the center."""
    jump(pen, x, y - radius)
    pen.setheading(0)
    pen.color(color)
    pen.fillcolor(color)
    pen.begin_fill()
    pen.circle(radius)
    pen.end_fill()
    pen.penup()


def line_segment(pen, x1, y1, x2, y2, color="black", width=2):
    pen.penup()
    pen.goto(x1, y1)
    pen.pendown()
    pen.pensize(width)
    pen.pencolor(color)
    pen.goto(x2, y2)
    pen.penup()


# -----------------------------
# LAB ALGORITHMS
# -----------------------------
def draw_pixel(pen, x, y, color, size=3):
    pen.penup()
    pen.goto(x, y)
    pen.dot(size, color)


def dda_line(pen, x1, y1, x2, y2, color="black", pixel_size=3):
    """Digital Differential Analyzer line algorithm."""
    dx = x2 - x1
    dy = y2 - y1
    steps = int(max(abs(dx), abs(dy)))

    if steps == 0:
        draw_pixel(pen, x1, y1, color, pixel_size)
        return

    x_increment = dx / steps
    y_increment = dy / steps

    x = x1
    y = y1

    for _ in range(steps + 1):
        draw_pixel(pen, round(x), round(y), color, pixel_size)
        x += x_increment
        y += y_increment


def bresenham_line(pen, x1, y1, x2, y2, color="black", pixel_size=3):
    """Bresenham line algorithm for all slopes."""
    x1, y1, x2, y2 = map(round, (x1, y1, x2, y2))

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    error = dx - dy

    while True:
        draw_pixel(pen, x1, y1, color, pixel_size)

        if x1 == x2 and y1 == y2:
            break

        error2 = 2 * error

        if error2 > -dy:
            error -= dy
            x1 += sx

        if error2 < dx:
            error += dx
            y1 += sy


def plot_circle_points(pen, xc, yc, x, y, color, pixel_size):
    points = [
        (xc + x, yc + y),
        (xc - x, yc + y),
        (xc + x, yc - y),
        (xc - x, yc - y),
        (xc + y, yc + x),
        (xc - y, yc + x),
        (xc + y, yc - x),
        (xc - y, yc - x),
    ]

    for px, py in points:
        draw_pixel(pen, px, py, color, pixel_size)


def midpoint_circle(pen, xc, yc, radius, color="black", pixel_size=3):
    """Midpoint circle drawing algorithm."""
    x = 0
    y = radius
    decision = 1 - radius

    while x <= y:
        plot_circle_points(pen, xc, yc, x, y, color, pixel_size)
        x += 1

        if decision < 0:
            decision += 2 * x + 1
        else:
            y -= 1
            decision += 2 * (x - y) + 1


# -----------------------------
# 2D TRANSFORMATIONS
# -----------------------------
def translate_point(point, tx, ty):
    x, y = point
    return x + tx, y + ty


def scale_point(point, sx, sy, origin=(0, 0)):
    x, y = point
    ox, oy = origin
    return ox + (x - ox) * sx, oy + (y - oy) * sy


def rotate_point(point, angle_degrees, origin=(0, 0)):
    x, y = point
    ox, oy = origin

    radians = math.radians(angle_degrees)
    translated_x = x - ox
    translated_y = y - oy

    rotated_x = translated_x * math.cos(radians) - translated_y * math.sin(radians)
    rotated_y = translated_x * math.sin(radians) + translated_y * math.cos(radians)

    return rotated_x + ox, rotated_y + oy


def reflect_point_x(point, axis_y=0):
    x, y = point
    return x, 2 * axis_y - y


def shear_point(point, shx=0.0, shy=0.0, origin=(0, 0)):
    x, y = point
    ox, oy = origin

    x -= ox
    y -= oy

    new_x = x + shx * y
    new_y = y + shy * x

    return new_x + ox, new_y + oy


# -----------------------------
# STATIC SCENE
# -----------------------------
def draw_ground_and_road():
    # Main green ground
    filled_rectangle(static_pen, -505, -355, 1010, 305, "#3C8D40")

    # Main asphalt road
    filled_rectangle(static_pen, -505, -290, 1010, 125, "#444444")

    # Green memorial zone behind the road
    filled_rectangle(static_pen, -505, -165, 1010, 125, "#3C8D40")

    # Footpath on the opposite side of the Shaheed Minar
    filled_rectangle(static_pen, -505, -355, 1010, 53, "#B8B8B8")
    filled_rectangle(static_pen, -505, -306, 1010, 5, "#E8E8E8")

    # Road borders using DDA
    dda_line(algorithm_pen, -500, -165, 500, -165, "white", 3)
    dda_line(algorithm_pen, -500, -290, 500, -290, "white", 3)

    # Road divider using Bresenham
    for x in range(-500, 500, 100):
        bresenham_line(
            algorithm_pen,
            x,
            -228,
            x + 55,
            -228,
            "#FFD700",
            4
        )

    # Steel boundary/fence behind the upper white road line
    fence_color = "#AEB6BF"

    line_segment(static_pen, -500, -132, 500, -132, fence_color, 3)
    line_segment(static_pen, -500, -100, 500, -100, fence_color, 3)

    for x in range(-490, 501, 35):
        line_segment(static_pen, x, -165, x, -88, fence_color, 3)


def draw_building(x, y, width, height, color):
    filled_rectangle(static_pen, x, y, width, height, color)

    # Roof gives a simple 3D appearance
    roof = [
        (x, y + height),
        (x + 25, y + height + 25),
        (x + width + 25, y + height + 25),
        (x + width, y + height),
    ]
    filled_polygon(static_pen, roof, "#6F4E37")

    # Side wall: fake 3D depth
    side = [
        (x + width, y),
        (x + width + 25, y + 20),
        (x + width + 25, y + height + 25),
        (x + width, y + height),
    ]
    filled_polygon(static_pen, side, "#8B6B61")

    # Windows
    for row in range(2):
        for col in range(2):
            wx = x + 18 + col * 42
            wy = y + 30 + row * 55
            filled_rectangle(static_pen, wx, wy, 22, 30, "#D9F1FF")


def draw_tree(x, y, scale=1.0):
    trunk_w = 22 * scale
    trunk_h = 90 * scale
    filled_rectangle(static_pen, x - trunk_w / 2, y, trunk_w, trunk_h, "#8B5A2B")

    filled_circle(static_pen, x, y + trunk_h + 35 * scale, 42 * scale, "#1F8A3B")
    filled_circle(static_pen, x - 32 * scale, y + trunk_h + 15 * scale, 33 * scale, "#228B22")
    filled_circle(static_pen, x + 32 * scale, y + trunk_h + 15 * scale, 33 * scale, "#228B22")


def draw_flagpole():
    """Steel flag stand placed close to the left side of Shaheed Minar."""
    pole_x = -205

    # Main steel pole
    for offset in range(4):
        dda_line(
            algorithm_pen,
            pole_x + offset,
            -72,
            pole_x + offset,
            175,
            "#7F8C8D",
            3
        )

    # Pole base
    filled_rectangle(static_pen, pole_x - 12, -78, 28, 8, "#626567")
    filled_circle(static_pen, pole_x + 2, 180, 7, "#7F8C8D")


def draw_shaheed_minar():
    """Draw a Shaheed Minar using stairs, a midpoint-filled red circle, and white pillars."""

    def draw_rect_with_border(x, y, w, h, fill_color):
        static_pen.penup()
        static_pen.goto(x, y)
        static_pen.setheading(0)
        static_pen.pendown()

        static_pen.color("black", fill_color)
        static_pen.begin_fill()

        for _ in range(2):
            static_pen.forward(w)
            static_pen.left(90)
            static_pen.forward(h)
            static_pen.left(90)

        static_pen.end_fill()
        static_pen.penup()

    def draw_circle_fill(xc, yc, x, y):
        static_pen.color("red")

        static_pen.penup()
        static_pen.goto(xc - x, yc + y)
        static_pen.pendown()
        static_pen.goto(xc + x, yc + y)

        static_pen.penup()
        static_pen.goto(xc - x, yc - y)
        static_pen.pendown()
        static_pen.goto(xc + x, yc - y)

        static_pen.penup()
        static_pen.goto(xc - y, yc + x)
        static_pen.pendown()
        static_pen.goto(xc + y, yc + x)

        static_pen.penup()
        static_pen.goto(xc - y, yc - x)
        static_pen.pendown()
        static_pen.goto(xc + y, yc - x)

        static_pen.penup()

    # Scale and position so the Shaheed Minar fits the existing scene.
    scale = 0.62
    x_shift = 55
    y_shift = 85

    def sx(value):
        return x_shift + value * scale

    def sy(value):
        return y_shift + value * scale

    # BASE & STAIRS
    draw_rect_with_border(sx(-300), sy(-220), 600 * scale, 70 * scale, "#7f7f7f")
    draw_rect_with_border(sx(-250), sy(-150), 500 * scale, 30 * scale, "#bfbfbf")
    draw_rect_with_border(sx(-200), sy(-120), 400 * scale, 25 * scale, "#d9d9d9")
    draw_rect_with_border(sx(-150), sy(-95), 300 * scale, 20 * scale, "#efefef")

    # MIDPOINT CIRCLE (FILLED)
    xc = sx(0)
    yc = sy(10)
    radius = int(100 * scale)

    x = 0
    y = radius
    pk = 1 - radius

    draw_circle_fill(xc, yc, x, y)

    while x < y:
        x += 1

        if pk < 0:
            pk = pk + 2 * x + 1
        else:
            y -= 1
            pk = pk + 2 * x - 2 * y + 1

        draw_circle_fill(xc, yc, x, y)

    # PILLARS
    draw_rect_with_border(sx(-15), sy(-95), 30 * scale, 260 * scale, "white")

    draw_rect_with_border(sx(-80), sy(-95), 25 * scale, 200 * scale, "white")
    draw_rect_with_border(sx(55), sy(-95), 25 * scale, 200 * scale, "white")

    draw_rect_with_border(sx(-140), sy(-95), 20 * scale, 150 * scale, "white")
    draw_rect_with_border(sx(120), sy(-95), 20 * scale, 150 * scale, "white")

    draw_rect_with_border(sx(-190), sy(-95), 15 * scale, 110 * scale, "white")
    draw_rect_with_border(sx(175), sy(-95), 15 * scale, 110 * scale, "white")

    # LABEL BELOW THE STRUCTURE
    static_pen.penup()
    static_pen.goto(sx(0), sy(-205))
    static_pen.color("black")
    static_pen.write(
        "Shaheed Minar",
        align="center",
        font=("Arial", 12, "bold"),
    )
    static_pen.penup()



def draw_far_tree_line():
    """Draw a soft distant tree line blended with the green memorial strip."""
    colors = ["#4F8F4D", "#579653", "#5E9C59", "#669F60"]

    # Tree canopies overlap the green strip so there is no visible gap.
    for index, x in enumerate(range(-520, 521, 28)):
        color = colors[index % len(colors)]
        radius = 17 + (index % 3) * 3
        center_y = -50 + (index % 2) * 4
        filled_circle(static_pen, x, center_y, radius, color)

    # A matching green base joins the distant trees to the main green line.
    filled_rectangle(static_pen, -500, -72, 1000, 24, "#4F8F4D")



def draw_foreground_trees():
    """Draw large trees partly outside the left, right, and lower frame."""

    # LEFT foreground tree
    filled_rectangle(static_pen, -535, -165, 48, 230, "#754C24")
    filled_circle(static_pen, -505, 105, 90, "#1F6F32")
    filled_circle(static_pen, -455, 125, 72, "#287D38")
    filled_circle(static_pen, -520, 175, 68, "#2D843C")
    filled_circle(static_pen, -445, 185, 58, "#347F3D")

    # RIGHT foreground tree — similar to the left side
    filled_rectangle(static_pen, 487, -165, 48, 230, "#754C24")
    filled_circle(static_pen, 505, 105, 90, "#1F6F32")
    filled_circle(static_pen, 455, 125, 72, "#287D38")
    filled_circle(static_pen, 520, 175, 68, "#2D843C")
    filled_circle(static_pen, 445, 185, 58, "#347F3D")





def draw_static_scene():
    static_pen.clear()
    algorithm_pen.clear()

    draw_ground_and_road()

    draw_far_tree_line()
    draw_foreground_trees()

    # Two large trees beside the Shaheed Minar
    draw_tree(-285, -70, 1.12)
    draw_tree(290, -70, 1.12)

    draw_shaheed_minar()
    draw_flagpole()

    # Lamp-post poles on the left and right sides
    draw_lamp_post_static(-430)
    draw_lamp_post_static(430)




def draw_light_focus(x):
    """Light reflection removed."""
    return


def draw_small_car(x, y, body_color, direction=1):
    """Draw a compact car. direction=1 faces right, -1 faces left."""
    black = "#151515"
    glass = "#CFEFFF"

    if direction == 1:
        body = [
            (x, y),
            (x + 145, y),
            (x + 145, y + 42),
            (x + 115, y + 42),
            (x + 95, y + 72),
            (x + 52, y + 72),
            (x + 28, y + 42),
            (x, y + 42),
        ]
        left_window = [
            (x + 42, y + 45),
            (x + 58, y + 66),
            (x + 78, y + 66),
            (x + 78, y + 45),
        ]
        right_window = [
            (x + 84, y + 45),
            (x + 84, y + 66),
            (x + 94, y + 66),
            (x + 108, y + 45),
        ]
        wheel1 = x + 36
        wheel2 = x + 112
    else:
        body = [
            (x, y),
            (x + 145, y),
            (x + 145, y + 42),
            (x + 117, y + 42),
            (x + 93, y + 72),
            (x + 50, y + 72),
            (x + 30, y + 42),
            (x, y + 42),
        ]
        left_window = [
            (x + 37, y + 45),
            (x + 51, y + 66),
            (x + 61, y + 66),
            (x + 61, y + 45),
        ]
        right_window = [
            (x + 67, y + 45),
            (x + 67, y + 66),
            (x + 88, y + 66),
            (x + 104, y + 45),
        ]
        wheel1 = x + 34
        wheel2 = x + 110

    filled_polygon(dynamic_pen, body, body_color)
    filled_polygon(dynamic_pen, left_window, glass)
    filled_polygon(dynamic_pen, right_window, glass)

    filled_circle(dynamic_pen, wheel1, y, 16, black)
    filled_circle(dynamic_pen, wheel2, y, 16, black)
    filled_circle(dynamic_pen, wheel1, y, 6, "#BFC9CA")
    filled_circle(dynamic_pen, wheel2, y, 6, "#BFC9CA")




def draw_lane_cars():
    """Upper lane red car moves left to right; lower lane yellow car moves right to left."""

    draw_small_car(upper_car_x, -202, "#E53935", direction=1)
    draw_small_car(lower_car_x, -258, "#F4D03F", direction=-1)


def draw_lamp_post_static(x):
    """Draw a lamp-post pole above the upper white road line."""
    pole_color = "#444B52"

    # Base and vertical pole
    filled_rectangle(static_pen, x - 9, -165, 18, 8, "#2F3337")
    line_segment(static_pen, x, -157, x, 45, pole_color, 6)

    # Curved-looking top arm made with line segments
    line_segment(static_pen, x, 45, x + (22 if x < 0 else -22), 65, pole_color, 5)
    line_segment(
        static_pen,
        x + (22 if x < 0 else -22),
        65,
        x + (38 if x < 0 else -38),
        65,
        pole_color,
        4
    )


def draw_lamp_light(x):
    """Lamp bulbs remain off in day and turn on in night mode."""
    bulb_x = x + (40 if x < 0 else -40)
    bulb_y = 62

    if is_night:
        # Glow
        filled_circle(dynamic_pen, bulb_x, bulb_y, 25, "#F3E7C8")
        filled_circle(dynamic_pen, bulb_x, bulb_y, 10, "#FFDFA3")
    else:
        filled_circle(dynamic_pen, bulb_x, bulb_y, 11, "#D5D8DC")


# -----------------------------
# DYNAMIC OBJECTS
# -----------------------------
def draw_sun_or_moon():
    """Show the sun in day mode and the crescent moon in night mode."""

    # Upper-right sky position
    sky_x = 390
    sky_y = 285

    if is_night:
        # Crescent moon
        filled_circle(dynamic_pen, sky_x, sky_y, 38, "#FFF6D5")
        filled_circle(
            dynamic_pen,
            sky_x + 15,
            sky_y + 12,
            35,
            "#101A3A"
        )
    else:
        # Daytime sun
        filled_circle(
            dynamic_pen,
            sky_x,
            sky_y,
            43,
            "#FFD700"
        )
        midpoint_circle(
            dynamic_pen,
            sky_x,
            sky_y,
            43,
            "#FF9F1C",
            3
        )


def draw_stars():
    if not is_night:
        return

    star_positions = [
        (-470, 300), (-440, 255), (-405, 325), (-370, 285),
        (-335, 235), (-305, 315), (-270, 270), (-235, 335),
        (-200, 250), (-165, 300), (-125, 225), (-90, 330),
        (-55, 275), (-20, 310), (20, 245), (55, 335),
        (90, 285), (125, 220), (160, 315), (195, 260),
        (230, 340), (265, 290), (300, 235), (335, 320),
        (370, 275), (405, 335), (440, 245), (475, 300)
    ]

    for index, (x, y) in enumerate(star_positions):
        size = 4 if index % 3 else 6
        dynamic_pen.goto(x, y)
        dynamic_pen.dot(size, "white")


def draw_cloud(x, y, scale=1.0, color=None):
    if color is None:
        color = "#F7F7F7" if not is_night else "#8E949B"

    filled_circle(dynamic_pen, x, y, 25 * scale, color)
    filled_circle(dynamic_pen, x + 30 * scale, y + 12 * scale, 34 * scale, color)
    filled_circle(dynamic_pen, x + 66 * scale, y, 27 * scale, color)
    filled_rectangle(dynamic_pen, x, y - 25 * scale, 66 * scale, 30 * scale, color)


def draw_clouds_scene():
    """Many bright clouds by day; only a few soft ash clouds at night."""
    if is_night:
        # Few soft ash-colored clouds
        draw_cloud(cloud_x + 40, 285, 0.75, "#8E949B")
        draw_cloud(cloud_x - 350, 320, 0.58, "#9AA0A6")
    else:
        # Many white clouds spread across the daytime sky
        draw_cloud(cloud_x, 275, 0.90, "#FFFFFF")
        draw_cloud(cloud_x - 250, 315, 0.65, "#FAFAFA")
        draw_cloud(cloud_x + 280, 325, 0.72, "#FFFFFF")
        draw_cloud(cloud_x - 500, 245, 0.55, "#F8F8F8")
        draw_cloud(cloud_x + 520, 245, 0.58, "#FFFFFF")


def draw_bird(x, y):
    flap = 10 + 8 * math.sin(wave_time * 3)

    # Bird wings use Bresenham lines
    bresenham_line(dynamic_pen, x, y, x + 18, y + flap, "#111111", 3)
    bresenham_line(dynamic_pen, x + 18, y + flap, x + 36, y, "#111111", 3)


def draw_waving_flag():
    pole_x = -205
    start_x = pole_x + 5
    start_y = 88

    # Smaller flag placed near Shaheed Minar
    width = 95
    height = 58
    strip_width = 4

    # Single rope connecting the flag to the stand
    line_segment(
        dynamic_pen,
        pole_x + 2,
        173,
        pole_x + 2,
        start_y + height - 3,
        "#E5E7E9",
        2
    )
    line_segment(
        dynamic_pen,
        pole_x + 2,
        start_y + height - 3,
        start_x + 3,
        start_y + height - 3,
        "#E5E7E9",
        2
    )

    # Waving green cloth
    for local_x in range(0, width, strip_width):
        wave = 5 * math.sin(wave_time + local_x * 0.12)
        shear = 0.035 * math.sin(wave_time)

        bottom_left = (start_x + local_x, start_y + wave)
        bottom_right = (start_x + local_x + strip_width + 1, start_y + wave)
        top_right = (
            start_x + local_x + strip_width + 1,
            start_y + height + wave
        )
        top_left = (start_x + local_x, start_y + height + wave)

        points = [bottom_left, bottom_right, top_right, top_left]
        points = [
            shear_point(p, shx=shear, origin=(start_x, start_y))
            for p in points
        ]

        filled_polygon(dynamic_pen, points, "#006A4E")

    circle_x = start_x + width * 0.44
    circle_y = start_y + height * 0.50
    circle_wave = 5 * math.sin(
        wave_time + width * 0.44 * 0.12
    )

    filled_circle(
        dynamic_pen,
        circle_x,
        circle_y + circle_wave,
        16,
        "#F42A41"
    )
    midpoint_circle(
        dynamic_pen,
        round(circle_x),
        round(circle_y + circle_wave),
        16,
        "#C8142F",
        2
    )


def draw_wheel(center_x, center_y, radius, angle):
    filled_circle(dynamic_pen, center_x, center_y, radius, "#151515")
    filled_circle(dynamic_pen, center_x, center_y, radius * 0.45, "#BBBBBB")

    # Rotating spokes demonstrate rotation.
    for base_angle in (0, 90):
        point = (center_x + radius * 0.8, center_y)
        rotated = rotate_point(point, angle + base_angle, origin=(center_x, center_y))
        opposite = rotate_point(point, angle + base_angle + 180, origin=(center_x, center_y))
        line_segment(dynamic_pen, opposite[0], opposite[1], rotated[0], rotated[1], "white", 2)


def draw_car(x, y):
    # Translation is represented by the changing x position.
    body_points = [
        (x, y),
        (x + 170, y),
        (x + 170, y + 50),
        (x + 140, y + 50),
        (x + 118, y + 88),
        (x + 63, y + 88),
        (x + 35, y + 50),
        (x, y + 50),
    ]

    filled_polygon(dynamic_pen, body_points, "#E53935")

    window_left = [(x + 49, y + 53), (x + 69, y + 80), (x + 91, y + 80), (x + 91, y + 53)]
    window_right = [(x + 98, y + 53), (x + 98, y + 80), (x + 115, y + 80), (x + 132, y + 53)]

    filled_polygon(dynamic_pen, window_left, "#BDE7F7")
    filled_polygon(dynamic_pen, window_right, "#BDE7F7")

    draw_wheel(x + 42, y, 19, wheel_angle)
    draw_wheel(x + 132, y, 19, wheel_angle)


def draw_reflection():
    """A reflected tree silhouette demonstrates reflection across a horizontal axis."""
    water_axis = -140
    original_points = [
        (-255, -55),
        (-285, -115),
        (-225, -115),
    ]

    reflected = [reflect_point_x(point, water_axis) for point in original_points]
    filled_polygon(dynamic_pen, reflected, "#2B6F4A")


def draw_firework(center_x, center_y, radius, color):
    for angle in range(0, 360, 24):
        end_x = center_x + radius * math.cos(math.radians(angle))
        end_y = center_y + radius * math.sin(math.radians(angle))
        dda_line(dynamic_pen, center_x, center_y, end_x, end_y, color, 3)


def draw_fireworks_scene():
    if not (is_night and show_fireworks):
        return

    draw_firework(70, 245, firework_radius, "#FF4D4D")
    draw_firework(-110, 285, firework_radius * 0.82, "#FFD700")
    draw_firework(255, 205, firework_radius * 0.70, "#5CE1E6")
    draw_firework(-330, 215, firework_radius * 0.58, "#FF66FF")
    draw_firework(390, 275, firework_radius * 0.62, "#7CFF6B")


def draw_labels():
    """Display keyboard controls."""
    text_pen.clear()
    text_pen.color("white" if is_night else "#183153")

    text_pen.goto(-485, -338)
    text_pen.write(
        "D/N: Day/Night | P: Pause all | F: Fireworks | "
        "Space: Car stop | Up/Down: Car speed | "
        "C: Cloud stop | V/B: Cloud +/- | "
        "G: Bird stop | H/J: Bird +/- | R: Reset | Esc: Exit",
        align="left",
        font=("Arial", 8, "normal"),
    )


# -----------------------------
# ANIMATION AND CONTROLS
# -----------------------------
def update_animation():
    global car_x, cloud_x, bird_x, wheel_angle, wave_time, firework_radius
    global upper_car_x, lower_car_x

    if not paused:
        car_x += car_speed

        if car_moving:
            upper_car_x += car_motion_speed
            lower_car_x -= car_motion_speed * 0.92

        if cloud_moving:
            cloud_x += cloud_speed

        if not is_night and birds_moving:
            bird_x += bird_speed

        wheel_angle -= car_motion_speed * 2 if car_moving else 0
        wave_time += 0.08

        if car_x > 520:
            car_x = -700

        if upper_car_x > 560:
            upper_car_x = -700

        if lower_car_x < -700:
            lower_car_x = 560

        if cloud_x > 560:
            cloud_x = -620

        if bird_x > 520:
            bird_x = -600

        if is_night:
            firework_radius += 1.4
            if firework_radius > 75:
                firework_radius = 5


    dynamic_pen.clear()

    draw_sun_or_moon()
    draw_stars()
    draw_clouds_scene()
    # Birds fly only during day mode
    if not is_night:
        draw_bird(bird_x, 150)
        draw_bird(bird_x - 100, 210)

    draw_waving_flag()

    # Lamps switch on automatically in night mode
    draw_light_focus(-430)
    draw_light_focus(430)
    draw_lamp_light(-430)
    draw_lamp_light(430)
    draw_lane_cars()
    draw_fireworks_scene()
    draw_labels()

    screen.update()
    screen.ontimer(update_animation, 30)


def set_day():
    global is_night
    is_night = False
    screen.bgcolor("#87CEEB")


def set_night():
    global is_night
    is_night = True
    screen.bgcolor("#101A3A")


def toggle_pause():
    global paused
    paused = not paused


def toggle_fireworks():
    global show_fireworks
    show_fireworks = not show_fireworks


def move_car_left():
    global car_x
    car_x -= 20


def move_car_right():
    global car_x
    car_x += 20


def increase_speed():
    global car_speed
    car_speed = min(car_speed + 1, 12)


def decrease_speed():
    global car_speed
    car_speed = max(car_speed - 1, 0)



def toggle_car_motion():
    global car_moving
    car_moving = not car_moving


def increase_car_motion_speed():
    global car_motion_speed
    car_motion_speed = min(car_motion_speed + 0.5, 10.0)


def decrease_car_motion_speed():
    global car_motion_speed
    car_motion_speed = max(car_motion_speed - 0.5, 0.5)


def toggle_cloud_motion():
    global cloud_moving
    cloud_moving = not cloud_moving


def increase_cloud_speed():
    global cloud_speed
    cloud_speed = min(cloud_speed + 0.3, 5.0)


def decrease_cloud_speed():
    global cloud_speed
    cloud_speed = max(cloud_speed - 0.3, 0.1)


def toggle_bird_motion():
    global birds_moving
    birds_moving = not birds_moving


def increase_bird_speed():
    global bird_speed
    bird_speed = min(bird_speed + 0.4, 7.0)


def decrease_bird_speed():
    global bird_speed
    bird_speed = max(bird_speed - 0.4, 0.4)


def reset_scene():
    global car_x, car_speed, cloud_x, bird_x
    global wheel_angle, wave_time, firework_radius
    global upper_car_x, lower_car_x
    global paused, is_night, show_fireworks
    global car_motion_speed, car_moving
    global cloud_speed, cloud_moving
    global bird_speed, birds_moving

    car_x = -520
    car_speed = 3
    cloud_x = -500
    bird_x = -450
    wheel_angle = 0
    wave_time = 0.0
    firework_radius = 5

    upper_car_x = -650
    lower_car_x = 650

    car_motion_speed = 2.6
    car_moving = True

    cloud_speed = 1.2
    cloud_moving = True

    bird_speed = 1.8
    birds_moving = True

    paused = False
    is_night = False
    show_fireworks = True
    screen.bgcolor("#87CEEB")


def close_program():
    screen.bye()


# -----------------------------
# PROGRAM START
# -----------------------------
draw_static_scene()

screen.listen()
screen.onkey(set_day, "d")
screen.onkey(set_day, "D")
screen.onkey(set_night, "n")
screen.onkey(set_night, "N")
screen.onkey(toggle_pause, "p")
screen.onkey(toggle_pause, "P")
screen.onkey(toggle_fireworks, "f")
screen.onkey(toggle_fireworks, "F")
screen.onkey(reset_scene, "r")
screen.onkey(reset_scene, "R")
screen.onkey(move_car_left, "Left")
screen.onkey(move_car_right, "Right")
screen.onkey(toggle_car_motion, "space")
screen.onkey(increase_car_motion_speed, "Up")
screen.onkey(decrease_car_motion_speed, "Down")

screen.onkey(toggle_cloud_motion, "c")
screen.onkey(toggle_cloud_motion, "C")
screen.onkey(increase_cloud_speed, "v")
screen.onkey(increase_cloud_speed, "V")
screen.onkey(decrease_cloud_speed, "b")
screen.onkey(decrease_cloud_speed, "B")

screen.onkey(toggle_bird_motion, "g")
screen.onkey(toggle_bird_motion, "G")
screen.onkey(increase_bird_speed, "h")
screen.onkey(increase_bird_speed, "H")
screen.onkey(decrease_bird_speed, "j")
screen.onkey(decrease_bird_speed, "J")
screen.onkey(close_program, "Escape")

update_animation()
screen.mainloop()