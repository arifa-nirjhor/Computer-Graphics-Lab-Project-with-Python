import turtle
import math
import random

# ============================================================
# Bangladesh National Parliament Scene - Python Turtle
# Based on the provided reference image

# Controls:
#   D       -> Day mode
#   N       -> Night mode
#   P       -> Pause / Resume
#   C       -> Stop / Start clouds
#   G       -> Stop / Start birds
#   B       -> Rain + storm clouds + lightning on / off
#   W / S   -> Bird speed up / down
#   E / Q   -> Cloud speed up / down
#   X / Z   -> Wind speed up / down (when it is not raining)
#   Space   -> Stop / Start red car
#   Left/Right -> Move red car manually
#   Up/Down -> Red car speed up / down
#   K       -> Stop / Start yellow car
#   J / L   -> Move yellow car manually
#   U / O   -> Yellow car speed down / up
#   R       -> Reset
#   Esc     -> Exit
# ============================================================

screen = turtle.Screen()
screen.title("Bangladesh National Parliament - Turtle Graphics")
screen.setup(width=1.0, height=1.0)
screen.setworldcoordinates(-500, -300, 500, 300)
screen.bgcolor("#2FA7EA")
screen.tracer(0) #Disable automatic animation

# -----------------------------
# GLOBAL STATE                |
# -----------------------------

is_night = False  #day mood
paused = False    #animation running
clouds_moving = True
birds_moving = True
red_car_moving = True
yellow_car_moving = True
rain_on = False

# Rain is remembered separately for day and night so toggling it in one
# mode never turns it on/off in the other mode.
rain_on_day = False
rain_on_night = False
thunder_on = True

# Sunset transition state: sky + clouds change gradually, sun sets, then moon rises

sunset_transition = False
sunset_step = 0
SUNSET_STEPS = 170  #total fram for completing the transition

# Night -> dawn -> morning -> noon transition

morning_transition = False
morning_step = 0
MORNING_STEPS = 300   #total fram for completing the transition

# Full-scene redraws are expensive in Turtle and cause moving objects to
# stutter. These three checkpoints retain the dawn -> morning -> noon
# atmosphere change without interrupting the car animation every few frames.
MORNING_SCENE_REFRESH_STEPS = (120, 205, 265)
DAY_SUN_X = 410  # Match the moon's fixed x-position.
DAY_SUN_Y = 245
DAY_SUN_RADIUS = 28

MORNING_SKY_COLORS = [
    "#10203D",  # deep night
    "#26365B",  # pre-dawn navy
    "#665274",  # violet dawn
    "#C46E78",  # rosy horizon
    "#F39A63",  # orange sunrise
    "#FFD6A0",  # soft golden morning
    "#A9D8EE",  # pale morning blue
    "#63B8E6",  # clear morning
    "#2FA7EA",  # bright noon blue
]

MORNING_SUN_COLORS = [
    "#FF7043",
    "#FF963F",
    "#FFC34D",
    "#FFD85A",
    "#FFD51B",
]

# Lamp lights stay OFF during sunset. They turn on only after full night,
# then brighten gradually.

light_level = 0.0
LIGHT_STEPS = 120
light_rising = False
light_step = 0
car_light_level = 0.0

# Smooth day -> sunset -> night blend.

night_level = 0.0
STARS_VISIBLE_AT = 0.68

# The colour used by the most recently painted static scene. Sunrise/sunset
# masks use this value so their foreground ground exactly matches the field.

static_scene_night_level = 0.0
moon_rising = False
moon_step = 0

MOON_STEPS = 120         # total frames the transition takes (slow, gradual sunset)

SUNSET_SKY_COLORS = [
    "#2FA7EA",  # daytime blue
    "#7FC2E0",
    "#FFD37A",  # golden hour
    "#FFA646",
    "#FF7A3C",  # orange
    "#E4573C",  # deep orange/red
    "#B14A6B",  # dusky pink/purple
    "#5F3E6E",
    "#2C2F5C",
    "#10203D",  # night navy
]

SUNSET_SUN_COLORS = [
    "#FFD51B",  # bright daytime sun
    "#FFC93B",
    "#FFA733",
    "#FF8C3C",
    "#FF6F3C",
    "#E4432B",  # deep red as it sinks
]

# Lightning animation state

lightning_visible = False
lightning_timer = 0
next_lightning = 45

cloud_x = -500
bird_x = -250
red_car_x = -520
yellow_car_x = 430

cloud_speed = 0.8
bird_speed = 1.0
red_car_speed = 2.2
yellow_car_speed = 2.2
wave_time = 0.0
wind_speed = 1.0

# Rain-drop positions: [x, y, speed, length]

rain_drops = [
    [
        random.randint(-500, 500),
        random.randint(-260, 300),
        random.uniform(7.0, 13.0),  #speed
        random.randint(9, 18),      #length
    ]
    for _ in range(400)
]

# -----------------------------
# TURTLES
# -----------------------------
static_pen = turtle.Turtle(visible=False)
static_pen.speed(0)
static_pen.penup()

dynamic_pen = turtle.Turtle(visible=False)
dynamic_pen.speed(0)
dynamic_pen.penup()

rain_pen = turtle.Turtle(visible=False)
rain_pen.speed(0)
rain_pen.penup()

lightning_pen = turtle.Turtle(visible=False)
lightning_pen.speed(0)
lightning_pen.penup()

# Dedicated layer for lamp/car lighting.
# Keeping light effects separate prevents them from disturbing the
# main moving-object drawing layer during fade-in.

light_pen = turtle.Turtle(visible=False)
light_pen.speed(0)
light_pen.penup()

# -----------------------------
# BASIC HELPERS
# -----------------------------

def jump(pen, x, y):    #using turtle, coordinate
    pen.penup()
    pen.goto(x, y)
    pen.pendown()

def rectangle(pen, x, y, w, h, fill, outline=None, width=1):
    pen.penup()
    pen.goto(x, y)
    pen.setheading(0)
    pen.pensize(width)
    pen.color(outline or fill, fill)  #outlone color
    pen.begin_fill()   #inside fill color
    pen.pendown()

    for length in (w, h, w, h):
        pen.forward(length)
        pen.left(90)

    pen.end_fill()
    pen.penup()

def polygon(pen, points, fill, outline=None, width=1):

    pen.penup()
    pen.goto(points[0])
    pen.pensize(width)
    pen.color(outline or fill, fill)
    pen.begin_fill()
    pen.pendown()

    for point in points[1:]:  #skip 1st point
        pen.goto(point)

    pen.goto(points[0])
    pen.end_fill()
    pen.penup()

def circle(pen, x, y, r, fill, outline=None, width=1):

    pen.penup()
    pen.goto(x, y-r)
    pen.setheading(0)
    pen.pensize(width)
    pen.color(outline or fill, fill)
    pen.begin_fill()
    pen.pendown()
    pen.circle(r)
    pen.end_fill()
    pen.penup()

def leafy_blob(pen, x, y, r, fill, outline=None, width=1, bumps=14, jitter=0.22):

    pen.penup()
    points = []
    n = bumps * 2     #create bump tree leaf

    for i in range(n):
        angle = (2 * math.pi * i) / n
        radius = r if i % 2 == 0 else r * (1 - jitter)
        px = x + radius * math.cos(angle)    #ciecle perametric equation
        py = y + radius * math.sin(angle)
        points.append((px, py))

    polygon(pen, points, fill, outline or fill, width)

def line(pen, x1, y1, x2, y2, color="black", width=2):

    pen.penup()
    pen.goto(x1, y1)
    pen.pendown()
    pen.pensize(width)
    pen.pencolor(color)
    pen.goto(x2, y2)
    pen.penup()

# -----------------------------
# COLOR GRADIENT HELPERS
# -----------------------------

def hex_to_rgb(h):
    h = h.lstrip("#")    #remove "#"
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c))) for c in rgb)

def mix_day_night(day_color, night_color, t=None):
    """Blend a day color into its night counterpart."""
    if t is None:
        t = night_level
    return lerp_color(day_color, night_color, max(0.0, min(1.0, t)))

def lerp_color(c1, c2, t):   #find a color between others 2
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex((r1 + (r2-r1)*t, g1 + (g2-g1)*t, b1 + (b2-b1)*t))

def gradient_color(colors, t):
    """Pick a color along a multi-stop gradient, t in [0, 1]."""
    t = max(0.0, min(1.0, t))
    segments = len(colors) - 1
    pos = t * segments
    index = min(int(pos), segments - 1)
    local_t = pos - index
    return lerp_color(colors[index], colors[index+1], local_t)

def ease_in_out(t):

    """Smoothstep easing: slow start, gentle middle, gentle finish -
    used so the whole sunset (sky + sun) advances at a natural,
    non-mechanical pace instead of a straight linear sweep."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

# -----------------------------
# STATIC SCENE
# -----------------------------

def draw_ground_and_road():
    # Environment palette changes between day and night.
    grass_color = mix_day_night("#53A63B", "#173F24")
    road_color = mix_day_night("#2F2F2F", "#121820")
    bottom_color = mix_day_night("#0A2C3B", "#07131C")
    edge_color = mix_day_night("#FFFFFF", "#87909A")
    divider_color = mix_day_night("#FFD229", "#A98922")

    # Green land
    rectangle(static_pen, -550, -65, 1050, 140, grass_color)

    # Road
    rectangle(static_pen, -550, -245, 1050, 180, road_color)

   # Bottom dark strip. Drawn far below y=-300 (down to -2000) so it always
    # fully covers the visible area even when a wider/taller-than-5:3 window
    # reveals extra world space below the original -300 boundary - otherwise
    # the screen's sky-colored background would show through as a stray
    # border at the bottom edge in fullscreen.
    rectangle(static_pen, -550, -2000, 1050, 1755, bottom_color)

    # Road edges
    line(static_pen, -550, -65, 500, -65, edge_color, 3)
    line(static_pen, -550, -245, 500, -245, edge_color, 3)

    # Yellow lane markers
    for x in range(-490, 500, 95):
        line(static_pen, x, -155, x+42, -155, divider_color, 3)

def draw_tree_line():
    tree_line_color = mix_day_night("#2C7D2D", "#102F1B")

    for x in range(-500, 501, 28):
        circle(static_pen, x, 86, 13, tree_line_color)
    rectangle(static_pen, -500, 72, 1000, 22, tree_line_color)

def draw_canopy(pen, x, y, scale, leaf_dark, leaf_mid, leaf_light, leaf_highlight, height_scale=1.0):

    clusters = [
        # dx, dy, radius, shade, bump-count
        (0,   74, 30, leaf_dark, 12),
        (-24, 67, 23, leaf_dark, 12),
        (24,  67, 23, leaf_dark, 12),
        (-40, 70, 16, leaf_mid, 9),
        (40,  70, 16, leaf_mid, 9),
        (-14, 90, 17, leaf_mid, 10),
        (14,  90, 17, leaf_mid, 10),
        (0,   62, 15, leaf_mid, 9),
        (-27, 80, 12, leaf_light, 8),
        (27,  80, 12, leaf_light, 8),
        (0,   96, 15, leaf_light, 9),
        (0,   80, 9,  leaf_highlight, 7),
        (-9, 100, 7,  leaf_highlight, 6),
        (10,  98, 7,  leaf_highlight, 6),
    ]

    r_scale = 1.0 + (height_scale - 1.0) * 0.4  # blobs grow a little too, not just spread apart

    for dx, dy, r, color, bumps in clusters:
        leafy_blob(pen, x + dx*scale, y + dy*scale*height_scale, r*scale*r_scale, color, bumps=bumps, jitter=0.3)

def draw_tree(x, y, scale=1.0, height_scale=1.0):
    trunk_color = mix_day_night("#7A4924", "#3E2B22")
    leaf_dark = mix_day_night("#2F7C2D", "#153B21")
    leaf_mid = mix_day_night("#2F8B2E", "#1A4828")
    leaf_light = mix_day_night("#4C9C31", "#24552D")
    leaf_highlight = mix_day_night("#84C24C", "#2E5A31")

    rectangle(
        static_pen,
        x-7*scale,
        y,
        14*scale,
        55*scale*height_scale,
        trunk_color
    )

    draw_canopy(static_pen, x, y, scale, leaf_dark, leaf_mid, leaf_light, leaf_highlight, height_scale)

def draw_tree_dynamic(x, y, scale=1.0, height_scale=1.0):

    """Same shape as draw_tree, but painted on the dynamic layer so it can
    sit in front of the setting sun and hide it as it sinks lower."""

    trunk_color = mix_day_night("#7A4924", "#3E2B22")
    leaf_dark = mix_day_night("#2F7C2D", "#153B21")
    leaf_mid = mix_day_night("#2F8B2E", "#1A4828")
    leaf_light = mix_day_night("#4C9C31", "#24552D")
    leaf_highlight = mix_day_night("#84C24C", "#2E5A31")

    rectangle(
        dynamic_pen,
        x-7*scale,
        y,
        14*scale,
        55*scale*height_scale,
        trunk_color
    )

    draw_canopy(dynamic_pen, x, y, scale, leaf_dark, leaf_mid, leaf_light, leaf_highlight, height_scale)

def draw_foliage_patch(x_min, x_max):
    """Repaints the ground and tree-line band on the dynamic layer, in
    front of the sun, so the sun visibly disappears behind BOTH the
    lighter green ground and the darker green tree line, instead of
    floating on top of them. Solid rectangles (no gaps between circles)
    are used here so no sliver of the sun can leak through the seam."""
    tree_line_color = mix_day_night("#2C7D2D", "#102F1B")
    grass_color = mix_day_night("#53A63B", "#173F24")

    # Lighter green ground, well above the fence so it isn't disturbed.
    rectangle(dynamic_pen, x_min, 30, x_max - x_min, 42, grass_color)

    # Darker green tree line band, drawn exactly like the original
    # draw_tree_line: bumpy circle tops, filled in by a solid rectangle
    # underneath so there are no gaps for the sun to leak through.

    for x in range(-500, 501, 28):
        if x_min - 20 <= x <= x_max + 20:
            circle(dynamic_pen, x, 86, 13, tree_line_color)
    rectangle(dynamic_pen, x_min, 72, x_max - x_min, 22, tree_line_color)

def draw_sun_horizon_overlay(x_min=335, x_max=475):
    """Redraw the green horizon in front of the sun.
    The grass colour comes from the last static redraw, so the small mask
    blends seamlessly into the existing field instead of showing as a block.
    """
    tree_line_color = mix_day_night(
        "#2C7D2D", "#102F1B", static_scene_night_level
    )
    grass_color = mix_day_night(
        "#53A63B", "#173F24", static_scene_night_level
    )
    # This covers the part of the sun that is below the tree line.  Its
    # colours match the static field precisely and it stays above the fence.
    rectangle(dynamic_pen, x_min, 30, x_max - x_min, 42, grass_color)

    for x in range(-500, 501, 28):
        if x_min - 20 <= x <= x_max + 20:
            circle(dynamic_pen, x, 86, 13, tree_line_color)
    rectangle(dynamic_pen, x_min, 72, x_max - x_min, 22, tree_line_color)

def draw_fence():
    c = mix_day_night("#EEEEEE", "#7D8791")

    line(static_pen, -500, -46, 500, -46, c, 3)
    line(static_pen, -500, -27, 500, -27, c, 2)
    line(static_pen, -500, -8, 500, -8, c, 2)

    for x in range(-490, 501, 36):
        line(static_pen, x, -65, x, 18, c, 3)
        circle(static_pen, x, 20, 4, c)

def draw_lamp_post(x, base_y=-65, top_y=130):
    # Stand: a wider flat foot plate plus a small block, so the post
    # reads as clearly planted in the ground instead of a bare line.
    rectangle(static_pen, x-10, base_y, 20, 6, "#2A2A2A", "#1A1A1A", 1)
    rectangle(static_pen, x-5, base_y+6, 10, 10, "#333333", "#1A1A1A", 1)
    line(static_pen, x, base_y+16, x, top_y, "#333333", 4)

    direction = 1 if x < 0 else -1
    line(static_pen, x, top_y, x + 18*direction, top_y+16, "#333333", 4)
    line(static_pen, x + 18*direction, top_y+16,
         x + 28*direction, top_y+16, "#333333", 3)

def draw_lamp_post_dynamic(x, base_y=-65, top_y=130):
    """Same shape as draw_lamp_post, redrawn on the dynamic layer so the
    sunset foliage patch (which passes through this area) never cuts
    through the pole or its stand."""
    rectangle(dynamic_pen, x-10, base_y, 20, 6, "#2A2A2A", "#1A1A1A", 1)
    rectangle(dynamic_pen, x-5, base_y+6, 10, 10, "#333333", "#1A1A1A", 1)
    line(dynamic_pen, x, base_y+16, x, top_y, "#333333", 4)

    direction = 1 if x < 0 else -1
    line(dynamic_pen, x, top_y, x + 18*direction, top_y+16, "#333333", 4)
    line(dynamic_pen, x + 18*direction, top_y+16,
         x + 28*direction, top_y+16, "#333333", 3)

def draw_stair_lamp(x, base_y):
    pole_color = mix_day_night("#252525", "#111416")
    bulb_color = mix_day_night("#F8E58A", "#8A793F")
    rectangle(static_pen, x-3, base_y, 6, 45, pole_color)

    polygon(
        static_pen,
        [(x-8, base_y+45), (x+8, base_y+45),
         (x+6, base_y+60), (x-6, base_y+60)],
        bulb_color, pole_color, 2
    )

    line(static_pen, x, base_y+60, x, base_y+67, pole_color, 2)

# -----------------------------
# PARLIAMENT BUILDING
# -----------------------------

def draw_parliament():
    cx = 0
    base = 40
    wall = mix_day_night("#DCC38B", "#75694F")
    wall2 = mix_day_night("#E8D09B", "#87795A")
    dark = mix_day_night("#6F665B", "#373A3C")
    glass = mix_day_night("#3A91BD", "#173F5A")
    outline = mix_day_night("#2C2C2C", "#161A1D")
    stair_color = mix_day_night("#7B3835", "#482A2B")
    stair_line = mix_day_night("#33211F", "#201719")
    wall_line = mix_day_night("#F0E0BE", "#9A8B69")
    entrance_color = mix_day_night("#28789D", "#123C55")

    # Stairs
    polygon(
        static_pen,
        [(-190, base), (190, base), (220, 8), (-220, 8)],
        stair_color, outline, 2
    )

    for y in range(12, 40, 5):
        spread = 190 + (40-y)*1.0
        line(static_pen, -spread, y, spread, y, stair_line, 1)

    # Main side wings
    rectangle(static_pen, -190, base, 95, 110, wall, outline, 2)
    rectangle(static_pen, 95, base, 95, 110, wall, outline, 2)

    # Inner blocks
    rectangle(static_pen, -95, base, 62, 135, wall2, outline, 2)
    rectangle(static_pen, 33, base, 62, 135, wall2, outline, 2)

    # Center block
    rectangle(static_pen, -33, base, 66, 135, wall2, outline, 2)

    # Upper crown
    polygon(
        static_pen,
        [(-100, 175), (-70, 200), (70, 200), (100, 175),
         (100, 145), (-100, 145)],
        wall2, outline, 2
    )

    # Crown divisions
    for x in (-70, -30, 25, 65):
        rectangle(static_pen, x, 148, 10, 52, wall, outline, 1)

    # Upper blue glass band
    rectangle(static_pen, -42, 158, 84, 28, glass, outline, 2)
    line(static_pen, 0, 158, 0, 186, outline, 1)
    line(static_pen, -42, 172, 42, 172, outline, 1)

    # Main entrance
    rectangle(static_pen, -18, base, 36, 48, entrance_color, outline, 2)
    line(static_pen, 0, base, 0, base+48, outline, 1)
    line(static_pen, -18, base+24, 18, base+24, outline, 1)

    # Circular windows
    for x in (-108, 108):
        circle(static_pen, x, 92, 16, dark, outline, 2)
        circle(static_pen, x, 92, 11, glass, outline, 1)

    # Triangular windows
    for x in (-165, -135, 135, 165):
        polygon(
            static_pen,
            [(x, 132), (x-8, 92), (x+8, 92)],
            dark, outline, 1
        )

        polygon(
            static_pen,
            [(x, 121), (x-4, 96), (x+4, 96)],
            glass, outline, 1
        )

    # Square windows (centered directly under each triangular window above)
    for tx in (-165, -135, 135, 165):
        x = tx - 9  # left edge, so the window's center lines up with the triangle's apex (tx)
        rectangle(static_pen, x, 58, 18, 28, glass, outline, 1)
        line(static_pen, x+9, 58, x+9, 86, outline, 1)
        line(static_pen, x, 72, x+18, 72, outline, 1)

    # Wall lines
    for y in range(56, 145, 10):
        line(static_pen, -188, y, -97, y, wall_line, 1)
        line(static_pen, 97, y, 188, y, wall_line, 1)

    # Roof flag pole
    line(static_pen, 0, 200, 0, 245, "#333333", 3)

    # Parliament lamp posts on the green field below both sides of the stairs
    draw_stair_lamp(-145, -2)
    draw_stair_lamp(145, -2)

# -----------------------------
# DYNAMIC OBJECTS
# -----------------------------
def draw_sun(x, y, radius, color, glow, glow_padding=8):
    """Draw the sun with its matching glow and body layers."""
    circle(dynamic_pen, x, y, radius + glow_padding, glow)
    circle(dynamic_pen, x, y, radius, color)

def draw_day_sun():
    """Draw the final daytime sun used after the dawn transition."""
    draw_sun(
        DAY_SUN_X,
        DAY_SUN_Y,
        DAY_SUN_RADIUS,
        MORNING_SUN_COLORS[-1],
        "#FFF1A8",
    )

def draw_sun_or_moon():
    # During rain, dense clouds cover the sun or moon.
    if rain_on:
        return

    if morning_transition:
        draw_morning_transition()
        return

    if sunset_transition:
        draw_sunset_sun()
        return

    if is_night:
        draw_rising_moon()
    else:
        # Use the exact same layered sun as the completed dawn transition.
        draw_day_sun()

def draw_sunset_moon(t):
    """Kept empty intentionally: moon must NOT appear during sunset."""
    return

def draw_rising_moon():
    """Moon stays fixed at its final night position.
    After full night, it fades in smoothly from invisible to fully visible.
    No vertical movement, no frame jump."""
    if not is_night:
        return

    p = ease_in_out(min(1.0, moon_step / MOON_STEPS))

    # Fixed final moon position.
    x, y = 410, 245
    radius = 26
    # Fade from the night-sky color to the final moon color.
    body = lerp_color("#10203D", "#FFF4C1", p)
    shadow = lerp_color("#10203D", "#10203D", p)

    circle(dynamic_pen, x, y, radius, body)

    # Crescent/shadow shape.
    circle(
        dynamic_pen,
        x + 10,
        y + 8,
        23,
        shadow
    )

def draw_morning_transition():
    """Fade the moon, then raise the sun through dawn into full daylight."""
    t = ease_in_out(min(1.0, morning_step / MORNING_STEPS))

    # The moon remains at its night position and slowly dissolves into the
    # changing dawn sky instead of dropping or jumping away.
    moon_fade = ease_in_out(min(1.0, t / 0.48))
    sky_color = gradient_color(MORNING_SKY_COLORS, t)
    if moon_fade < 1.0:
        moon_body = lerp_color("#FFF4C1", sky_color, moon_fade)
        draw_sun(410, 245, 26, moon_body, sky_color, glow_padding=0)
        circle(dynamic_pen, 420, 253, 23, sky_color)

    # After the moon has faded, the sun rises from the same right-side
    # horizon where it set, then the scene continues to morning and noon.
    sun_start = 0.48
    sun_t = ease_in_out(max(0.0, min(1.0, (t - sun_start) / (1.0 - sun_start))))

    if sun_t > 0.0:
        sun_x = DAY_SUN_X
        sunrise_start_y = 58
        sun_y = sunrise_start_y + (DAY_SUN_Y - sunrise_start_y) * sun_t
        radius = 17 + (DAY_SUN_RADIUS - 17) * sun_t
        sun_color = gradient_color(MORNING_SUN_COLORS, sun_t)
        glow = lerp_color("#F28B61", "#FFF1A8", sun_t)
        draw_sun(sun_x, sun_y, radius, sun_color, glow)

        # Keep the rising sun behind the green horizon until it clears it.
        if sun_y - (radius + 8) < 100:
            draw_sun_horizon_overlay()

        # The nearby trees stay in front until the sun fully clears their
        # (now taller) canopy tops, so it never visibly pokes out in front
        # of them partway through the rise.
        if sun_y - (radius + 8) < 205:
            draw_tree_dynamic(405, 72, 0.45, 1.3)
            draw_tree_dynamic(470, 70, 0.9, 1.3)

        # The lamp is always redrawn after the sun, keeping it visually in
        # front even during the sunrise animation.
        draw_lamp_post_dynamic(360)

def draw_sunset_sun():
    """Sun slowly slides down and sinks completely behind the green tree line.
    Uses the same eased timeline as the sky so the sun's motion, size, and
    color always stay in sync with how the atmosphere is changing.
    Ekই function-er modhye, sunset-er dhitiyardho theke, thik shei
    jaygay theke chad uthte shuru kore (draw_sunset_moon)."""

    t = ease_in_out(sunset_step / SUNSET_STEPS)

    # Start exactly where the daytime sun is already drawn.  This avoids
    # the visual jump to the right when N starts the sunset animation.
    start_x, start_y = DAY_SUN_X, DAY_SUN_Y
    end_x, end_y = DAY_SUN_X, 64       # same right-side horizon as sunrise

    x = start_x + (end_x - start_x) * t
    y = start_y + (end_y - start_y) * t

    radius = 28 - 20 * t              # shrinks a little as it sets
    color = gradient_color(SUNSET_SUN_COLORS, t)
    # Soft glow halo, fades as the sky darkens.
    glow_color = gradient_color(
        ["#FFF4C1", "#FFD9A0", "#E68A6B", "#7A4B5C"], t
    )

    draw_sun(x, y, radius, color, glow_color, glow_padding=10)
    # Keep the setting sun behind the same green horizon used at sunrise.
    if y - (radius + 10) < 100:
        draw_sun_horizon_overlay()
    # Repaint the actual right-side trees on top of the sun.
    draw_lamp_post_dynamic(360)
    draw_tree_dynamic(405, 72, 0.45, 1.3)
    draw_tree_dynamic(470, 70, 0.9, 1.3)

def draw_cloud(x, y, scale=1.0, color=None):
    """Draw one layered cloud."""
    if color is None:
        if rain_on:
            color = "#858B91" if not is_night else "#555E68"
        else:
            color = "#8E949B" if is_night else "white"

    # Extra back layer produces a soft, dense cloud.
    back_color = (
        "#737A80" if not is_night else "#414A55"
    ) if rain_on else color
    if rain_on:
        circle(dynamic_pen, x-8*scale, y+3*scale, 18*scale, back_color)
        circle(dynamic_pen, x+14*scale, y+12*scale, 23*scale, back_color)
        circle(dynamic_pen, x+40*scale, y+6*scale, 21*scale, back_color)
        circle(dynamic_pen, x+62*scale, y+3*scale, 17*scale, back_color)
        rectangle(
            dynamic_pen,
            x-8*scale,
            y-14*scale,
            70*scale,
            23*scale,
            back_color
        )
    # Front cloud layer
    circle(dynamic_pen, x, y, 13*scale, color)
    circle(dynamic_pen, x+18*scale, y+7*scale, 18*scale, color)
    circle(dynamic_pen, x+38*scale, y, 14*scale, color)
    rectangle(dynamic_pen, x, y-10*scale, 38*scale, 15*scale, color)

def get_atmosphere_cloud_color():
    """Return cloud color that follows the current sky atmosphere.
    During sunset it smoothly changes white -> warm gold/orange ->
    dusky purple -> night gray-blue."""
    if sunset_transition:
        t = ease_in_out(sunset_step / SUNSET_STEPS)
        if t < 0.15:
            c1, c2, local = "#FFFFFF", "#E9EEF0", t / 0.15
        elif t < 0.35:
            c1, c2, local = "#E9EEF0", "#FFD59A", (t - 0.15) / 0.20
        elif t < 0.55:
            c1, c2, local = "#FFD59A", "#F28A67", (t - 0.35) / 0.20
        elif t < 0.75:
            c1, c2, local = "#F28A67", "#A65B79", (t - 0.55) / 0.20
        else:
            c1, c2, local = "#A65B79", "#606A78", (t - 0.75) / 0.25

        return lerp_color(c1, c2, local)

    if rain_on:
        return "#8A9096" if not is_night else "#59616B"
    return "#777E86" if is_night else "white"

def draw_clouds():
    if rain_on:
        # Dense storm clouds repeat continuously across the sky.
        cloud_color = get_atmosphere_cloud_color()
        repeat_width = 950
        cloud_pattern = [
            (-80, 292, 1.10),
            (25, 300, 1.03),
            (130, 288, 1.12),
            (235, 301, 1.04),
            (340, 289, 1.14),
            (445, 300, 1.05),
            (550, 288, 1.12),
            (655, 300, 1.04),
            (760, 289, 1.12),
            (865, 300, 1.05),
            (-25, 258, 1.02),
            (90, 266, 1.08),
            (205, 255, 1.00),
            (320, 267, 1.09),
            (435, 255, 1.02),
            (550, 266, 1.08),
            (665, 255, 1.01),
            (780, 266, 1.08),
        ]

        for offset in (-repeat_width, 0, repeat_width):
            for local_x, y, scale in cloud_pattern:
                draw_cloud(
                    cloud_x + offset + local_x,
                    y,
                    scale,
                    cloud_color
                )

    elif morning_transition:
        # Dawn clouds change from bluish-grey to soft peach and then white.
        t = ease_in_out(morning_step / MORNING_STEPS)
        dawn_cloud = gradient_color(
            ["#697486", "#A8899A", "#E8B49B", "#F4E1D2", "#FFFFFF"], t
        )
        draw_cloud(cloud_x, 286, 0.82, dawn_cloud)
        draw_cloud(cloud_x+245, 304, 0.52, dawn_cloud)
        draw_cloud(cloud_x+470, 292, 0.64, dawn_cloud)
        draw_cloud(cloud_x+720, 304, 0.52, dawn_cloud)

    elif sunset_transition:
        # During sunset the clouds follow the same atmosphere as the sky.
        cloud_color = get_atmosphere_cloud_color()
        draw_cloud(cloud_x, 286, 0.82, cloud_color)
        draw_cloud(cloud_x+245, 304, 0.52, cloud_color)
        draw_cloud(cloud_x+470, 292, 0.64, cloud_color)
        draw_cloud(cloud_x+720, 304, 0.52, cloud_color)

    elif is_night:
        # Normal night clouds: few, ash-coloured, and high in the sky.
        draw_cloud(cloud_x+20, 282, 0.76, "#777E86")
        draw_cloud(cloud_x+340, 294, 0.62, "#858B92")
        draw_cloud(cloud_x+670, 276, 0.70, "#747B83")

    else:
        # Normal daytime clouds: white and high in the sky.
        draw_cloud(cloud_x, 286, 0.82, "white")
        draw_cloud(cloud_x+245, 304, 0.52, "#FAFAFA")
        draw_cloud(cloud_x+470, 292, 0.64, "white")
        draw_cloud(cloud_x+720, 304, 0.52, "#FAFAFA")

def draw_bird(x, y, scale=1.0):
    flap = 5*math.sin(wave_time*3)
    line(dynamic_pen, x-9*scale, y+flap, x, y-3*scale, "#151515", 1.5)
    line(dynamic_pen, x, y-3*scale, x+9*scale, y+flap, "#151515", 1.5)

def draw_birds():
    # Birds leave the sky exactly when the first stars become visible.
    if night_level >= STARS_VISIBLE_AT or rain_on:
        return

    positions = [
        (bird_x, 225), (bird_x+35, 218), (bird_x+65, 210),
        (bird_x+20, 198), (bird_x+50, 190)
    ]

    for i, (x, y) in enumerate(positions):
        draw_bird(x, y, 0.55 + 0.05*(i%2))

def draw_flag():
    """Draw the Bangladesh flag with wind-controlled animation."""
    x0 = 4
    y0 = 215
    width = 44
    height = 24
    # Two thin ropes connect the flag to the roof pole.
    rope_color = "#E5E1D2" if not is_night else "#AEB5B8"
    pole_x = 0
    top_attach_y = y0 + height - 2
    bottom_attach_y = y0 + 2

    line(dynamic_pen, pole_x + 1, 243, pole_x + 1, bottom_attach_y, rope_color, 1)
    line(dynamic_pen, pole_x + 1, top_attach_y, x0 + 2, top_attach_y, rope_color, 1)
    line(dynamic_pen, pole_x + 1, bottom_attach_y, x0 + 2, bottom_attach_y, rope_color, 1)

    # Manual wind controls the flag when rain is off.
    active_wind = wind_speed
    # Stronger wind creates larger and faster waves.
    wave_amplitude = 2.0 + active_wind * 2.2
    wave_frequency = 0.17 + active_wind * 0.055
    horizontal_stretch = 1.0 + min(active_wind, 5.0) * 0.05
    strip_width = 4
    stretched_width = width * horizontal_stretch

    for dx in range(0, int(stretched_width), strip_width):
        wave = wave_amplitude * math.sin(
            wave_time * (0.8 + active_wind * 0.45)
            + dx * wave_frequency
        )
        # Slight backward lift makes the flag look strongly wind-blown.
        lift = (dx / max(stretched_width, 1)) * active_wind * 1.2
        polygon(
            dynamic_pen,
            [
                (x0 + dx, y0 + wave + lift),
                (x0 + dx + strip_width + 1, y0 + wave + lift),
                (
                    x0 + dx + strip_width + 1,
                    y0 + height + wave + lift
                ),
                (x0 + dx, y0 + height + wave + lift),
            ],
            "#006A4E",
        )

    circle_x = x0 + stretched_width * 0.45
    circle_wave = wave_amplitude * math.sin(
        wave_time * (0.8 + active_wind * 0.45)
        + stretched_width * 0.45 * wave_frequency
    )
    circle_lift = 0.45 * active_wind

    circle(
        dynamic_pen,
        circle_x,
        y0 + height * 0.5 + circle_wave + circle_lift,
        7,
        "#F42A41",
    )

def draw_lamp_glow(x, top_y=146):
    """Large circular focus centered exactly on the lamp head.
    The focus stays local to the lamp and does not project onto the road/sky."""
    direction = 1 if x < 0 else -1
    bx = x + 28 * direction
    by = top_y

    if light_level <= 0.0:
        light_pen.goto(bx, by)
        light_pen.dot(5, "#F2F2F2")
        return

    # Large concentric circular focus.
    light_pen.goto(bx, by)
    light_pen.dot(58, "#4F4A31")      # large soft outer halo
    light_pen.goto(bx, by)
    light_pen.dot(46, "#71643A")      # broad warm focus
    light_pen.goto(bx, by)
    light_pen.dot(32, "#9C8946")      # stronger inner focus
    light_pen.goto(bx, by)
    light_pen.dot(19, "#D0B75F")      # bright inner ring
    light_pen.goto(bx, by)
    light_pen.dot(9, "#FFF1A3")       # lamp core
def draw_parliament_lamp_glow(x, base_y=-2):
    """Small Parliament lamps: smooth bulb + compact focused glow."""
    bulb_y = base_y + 53
    if light_level <= 0.0:
        light_pen.goto(x, bulb_y)
        light_pen.dot(4, "#F5E7A0")
        return

    glow = ease_in_out(max(0.0, min(1.0, light_level)))
    halo_color = lerp_color("#969696", "#9D8A45", glow)
    bulb_color = lerp_color("#E5E5E5", "#FFF4A8", glow)
    light_pen.goto(x, bulb_y)
    light_pen.dot(7 + int(9 * glow), halo_color)
    light_pen.goto(x, bulb_y)
    light_pen.dot(4, bulb_color)

def draw_car(x, y, color, direction=1):
    black = mix_day_night("#111111", "#080A0C")
    glass = mix_day_night("#BCEAF6", "#446071")
    if color == "#E53935":
        color = mix_day_night("#E53935", "#7D2428")
    elif color == "#F4C536":
        color = mix_day_night("#F4C536", "#8D7422")

    if direction == 1:
        body = [
            (x, y), (x+100, y), (x+100, y+28), (x+78, y+28),
            (x+62, y+50), (x+30, y+50), (x+15, y+28), (x, y+28)
        ]
        front_window = [
            (x+48, y+31), (x+68, y+31),
            (x+60, y+46), (x+48, y+46)
        ]
        rear_window = [
            (x+28, y+31), (x+45, y+31),
            (x+45, y+46), (x+33, y+46)
        ]
    else:
        body = [
            (x, y), (x+100, y), (x+100, y+28), (x+85, y+28),
            (x+70, y+50), (x+38, y+50), (x+22, y+28), (x, y+28)
        ]
        # corrected front window for left-facing yellow car
        front_window = [
            (x+22, y+31), (x+40, y+31),
            (x+40, y+46), (x+32, y+46)
        ]
        rear_window = [
            (x+44, y+31), (x+68, y+31),
            (x+62, y+46), (x+44, y+46)
        ]

    polygon(dynamic_pen, body, color, color)
    polygon(dynamic_pen, front_window, glass, glass)
    polygon(dynamic_pen, rear_window, glass, glass)
    circle(dynamic_pen, x+24, y, 12, black)
    circle(dynamic_pen, x+76, y, 12, black)

    hub_color = mix_day_night("#BEC4C7", "#70787D")
    circle(dynamic_pen, x+24, y, 5, hub_color)
    circle(dynamic_pen, x+76, y, 5, hub_color)

    # Headlights turn on with the stars and stay on through early dawn.
    if car_light_level > 0.0:
        head_alpha = car_light_level
        head_color = lerp_color("#B8B8B8", "#FFF0A3", head_alpha)
        glow_color = lerp_color("#777777", "#5F5A32", head_alpha)
        if direction == 1:
            head_x = x + 99
            light_pen.goto(head_x, y + 22)
            light_pen.dot(4, head_color)
            polygon(
                light_pen,
                [(head_x+2, y+25), (head_x+38, y+34),
                 (head_x+38, y+10), (head_x+2, y+19)],
                glow_color
            )
        else:
            head_x = x + 1
            light_pen.goto(head_x, y + 22)
            light_pen.dot(4, head_color)
            polygon(
                light_pen,
                [(head_x-2, y+25), (head_x-38, y+34),
                 (head_x-38, y+10), (head_x-2, y+19)],
                glow_color
            )

def draw_cars():
    # Red car moves in the upper black-road lane, above the yellow divider.
    draw_car(red_car_x, -118, "#E53935", 1)
    # Yellow car moves from right to left in the lower lane.
    draw_car(yellow_car_x, -205, "#F4C536", -1)

def draw_stars():
    # Stars gradually appear as the sky becomes dark; hidden in rain.
    if rain_on or night_level < STARS_VISIBLE_AT:
        return
    star_alpha = (night_level - STARS_VISIBLE_AT) / (1.0 - STARS_VISIBLE_AT)
    star_size = max(1, int(1 + 3 * star_alpha))
    for x, y in [
        (-430,260), (-350,220), (-260,250),
        (-160,230), (-60,265), (80,245),
        (190,270), (300,230), (450,255)
    ]:

        dynamic_pen.goto(x, y)
        dynamic_pen.dot(star_size, "white")

def draw_rainy_atmosphere():
    """Add an overcast, misty atmosphere during daytime rain."""
    if not rain_on or is_night:
        return
    # Soft horizontal haze bands in the sky.
    haze_colors = ["#91A7B3", "#9EAFB8", "#859DAA"]
    for index, y in enumerate((285, 270, 250, 230, 205, 180, 150)):
        color = haze_colors[index % len(haze_colors)]
        for x in range(-500 + (index % 2) * 35, 500, 115):
            line(dynamic_pen, x, y, x + 72, y - 4, color, 2)
    # Small mist particles create a wet, gloomy look.

    mist_points = [
        (-430, 170), (-350, 245), (-280, 200), (-190, 280),
        (-100, 225), (-20, 265), (75, 190), (155, 250),
        (245, 205), (330, 275), (420, 220)
    ]

    for x, y in mist_points:
        dynamic_pen.penup()
        dynamic_pen.goto(x, y)
        dynamic_pen.dot(6, "#AABAC1")

def draw_lightning_bolt(x, y, scale=1.0):
    """Draw a bright zigzag lightning bolt."""
    points = [
        (x, y),
        (x - 14*scale, y - 34*scale),
        (x + 1*scale, y - 31*scale),
        (x - 19*scale, y - 72*scale),
        (x + 20*scale, y - 24*scale),
        (x + 5*scale, y - 27*scale),
    ]

    lightning_pen.penup()
    lightning_pen.goto(points[0])
    lightning_pen.pendown()
    lightning_pen.pensize(max(2, int(5*scale)))
    lightning_pen.pencolor("#FFF7A8")

    for point in points[1:]:
        lightning_pen.goto(point)

    lightning_pen.penup()

    # Thin white center makes the bolt glow.
    lightning_pen.goto(points[0])
    lightning_pen.pendown()
    lightning_pen.pensize(max(1, int(2*scale)))
    lightning_pen.pencolor("white")

    for point in points[1:]:
        lightning_pen.goto(point)
    lightning_pen.penup()

def update_lightning():
    """Random lightning flashes only while rain is active."""
    global lightning_visible, lightning_timer, next_lightning
    lightning_pen.clear()

    # Lightning appears automatically only during rain.
    if not rain_on:
        lightning_pen.clear()
        lightning_visible = False
        lightning_timer = 0
        return
    lightning_timer += 1
    # Begin a new flash at a semi-random interval.
    if not lightning_visible and lightning_timer >= next_lightning:
        lightning_visible = True
        lightning_timer = 0
        next_lightning = random.randint(35, 95)

    if lightning_visible:
        # Draw one or two bolts from dense clouds.
        bolt_x = random.choice([-300, -170, -40, 110, 250, 360])
        draw_lightning_bolt(bolt_x, random.randint(245, 285), random.uniform(0.8, 1.2))
        if random.random() < 0.35:
            draw_lightning_bolt(
                bolt_x + random.randint(70, 150),
                random.randint(235, 275),
                random.uniform(0.65, 0.95),
            )
        # Brief sky flash works in both day and night modes.
        if lightning_timer <= 1:
            screen.bgcolor("#DCEBEE" if not is_night else "#66738E")

        # Keep the lightning visible for a few frames.
        if lightning_timer >= 4:
            lightning_visible = False
            lightning_timer = 0
            screen.bgcolor(
                "#66899B" if (rain_on and not is_night)
                else "#0B1426" if (rain_on and is_night)
                else "#2FA7EA" if not is_night
                else "#10203D"
            )

def draw_rain():
    """Draw and animate rain when rain_on is True."""
    rain_pen.clear()
    if not rain_on:
        return

    rain_pen.pencolor("#B8DCF0" if not is_night else "#7598B5")
    rain_pen.pensize(2)

    for drop in rain_drops:
        x, y, speed, length = drop
        rain_pen.penup()
        rain_pen.goto(x, y)
        rain_pen.pendown()
        storm_slant = 12 if rain_on else 4
        rain_pen.goto(x - storm_slant, y - length)
        rain_pen.penup()
        drop[1] -= speed

        # Restart the drop at the top after it falls below the screen.
        if drop[1] < -280:
            drop[0] = random.randint(-500, 500)
            drop[1] = random.randint(260, 330)
            drop[2] = random.uniform(7.0, 13.0)
            drop[3] = random.randint(9, 18)

def toggle_rain():
    """Press B to toggle rain, dense clouds, and automatic lightning."""
    global rain_on, rain_on_day, rain_on_night
    global lightning_visible, lightning_timer

    rain_on = not rain_on
    # Remember this rain state only for the mode we're currently in, so
    # switching to the other mode later never inherits it.
    if is_night:
        rain_on_night = rain_on
    else:
        rain_on_day = rain_on
    if rain_on:
        # Day rain uses a grey-blue overcast sky.
        screen.bgcolor("#66899B" if not is_night else "#0B1426")
    else:
        rain_pen.clear()
        lightning_pen.clear()
        lightning_visible = False
        lightning_timer = 0
        screen.bgcolor("#2FA7EA" if not is_night else "#10203D")

    draw_static_scene()


def toggle_thunder():
    """Press T to toggle thunder and lightning independently."""
    global thunder_on
    global lightning_visible, lightning_timer
    thunder_on = not thunder_on

    if not thunder_on:
        lightning_pen.clear()
        lightning_visible = False
        lightning_timer = 0
        screen.bgcolor("#2FA7EA" if not is_night else "#10203D")

# -----------------------------
# ANIMATION
# -----------------------------
def update():
    global cloud_x, bird_x, red_car_x, yellow_car_x, wave_time
    global sunset_transition, sunset_step, is_night, night_level, moon_rising, moon_step
    global morning_transition, morning_step
    global light_level, light_rising, light_step, car_light_level
    global rain_on

    if morning_transition and not paused:
        morning_step += 1
        t = ease_in_out(min(1.0, morning_step / MORNING_STEPS))
        # Night colours gradually disappear while dawn becomes morning and noon.
        night_level = 1.0 - t
        screen.bgcolor(gradient_color(MORNING_SKY_COLORS, t))
        # Lamps and car headlights remain fully ON while the sun is still
        # below/inside the tree-line horizon. The moment the whole sun enters
        # the open sky, both kinds of lights switch OFF together.
        sun_start = 0.48
        raw_sun_t = max(0.0, min(1.0, (t - sun_start) / (1.0 - sun_start)))
        sun_t = ease_in_out(raw_sun_t)
        sunrise_start_y = 58
        sun_y = sunrise_start_y + (DAY_SUN_Y - sunrise_start_y) * sun_t
        sun_radius = 17 + (DAY_SUN_RADIUS - 17) * sun_t
        # Keep lights on through the starry part of dawn.  They switch off
        # exactly when the stars disappear, not immediately when D is pressed.
        lights_should_be_on = night_level >= STARS_VISIBLE_AT
        light_level = 1.0 if lights_should_be_on else 0.0
        car_light_level = light_level
        # Keep the sky gradient smooth every frame, but repaint the costly
        # ground/building/tree layer only at the three visual time-of-day
        # milestones.  Cars remain on the lightweight dynamic layer.
        if morning_step in MORNING_SCENE_REFRESH_STEPS:
            draw_static_scene()
        if morning_step >= MORNING_STEPS:
            morning_transition = False
            morning_step = 0
            is_night = False
            night_level = 0.0
            light_level = 0.0
            car_light_level = 0.0
            # Day mode uses its own remembered rain state, independent of
            # whatever was raining in night mode.
            rain_on = rain_on_day
            screen.bgcolor("#66899B" if rain_on else "#2FA7EA")
            # Do not redraw the full static scene on this boundary frame.
            # It was already painted almost identically a few frames ago;
            # skipping the duplicate expensive work prevents the cars from
            # stuttering exactly as the sun reaches its final position.

    elif sunset_transition and not paused:
        sunset_step += 1
        t = ease_in_out(sunset_step / SUNSET_STEPS)
        night_level = t
        # Birds vanish and lamp/car lights turn on with the first stars.
        lights_should_be_on = night_level >= STARS_VISIBLE_AT
        light_level = 1.0 if lights_should_be_on else 0.0
        car_light_level = light_level
        # Sky + clouds + ground + building colors all move toward night together.
        atmosphere_color = gradient_color(SUNSET_SKY_COLORS, t)
        screen.bgcolor(atmosphere_color)
        # Redraw the static scene using the current day/night blend.
        if sunset_step % 3 == 0:
            draw_static_scene()
        if sunset_step >= SUNSET_STEPS:
            # Full night keeps the lights that already turned on with stars.
            sunset_transition = False
            sunset_step = 0
            is_night = True
            night_level = 1.0

            light_rising = False
            light_step = LIGHT_STEPS
            light_level = 1.0
            car_light_level = 1.0

            moon_rising = True
            moon_step = 0
            # Night mode uses its own remembered rain state, independent of
            # whatever was raining in day mode.
            rain_on = rain_on_night
            screen.bgcolor("#0B1426" if rain_on else "#10203D")
            draw_static_scene()

    elif not sunset_transition and is_night and not paused:
        # Full-night animations share the same frame/update pass.
        # This avoids phase switching that can look like a dropped frame.
        if light_rising:
            light_step += 1
            light_level = ease_in_out(min(1.0, light_step / LIGHT_STEPS))
            car_light_level = light_level

            if light_step >= LIGHT_STEPS:
                light_step = LIGHT_STEPS
                light_level = 1.0
                car_light_level = 1.0
                light_rising = False

        if moon_rising:
            moon_step += 1
            if moon_step >= MOON_STEPS:
                moon_step = MOON_STEPS
                moon_rising = False

    if not paused:
        wave_time += 0.16 if rain_on else (0.06 + wind_speed * 0.025)
        if clouds_moving:
            # Strong storm wind pushes clouds much faster during rain.
            storm_multiplier = 2.8 if rain_on else 1.0
            cloud_x += cloud_speed * storm_multiplier
            if rain_on:
                # Seamless wrap: preserve movement instead of jumping/resetting.
                if cloud_x >= 950:
                    cloud_x -= 950
            else:
                if cloud_x > 520:
                    cloud_x = -650
        if birds_moving and night_level < STARS_VISIBLE_AT:
            bird_x += bird_speed
            if bird_x > 420:
                bird_x = -350

        car_factor = 1.0
        if sunset_transition:
            progress = sunset_step / SUNSET_STEPS
            car_factor = 1.0 + 0.35 * ease_in_out(progress)
        elif is_night:
            car_factor = 1.10

        if red_car_moving:
            red_car_x += red_car_speed * car_factor
            if red_car_x > 520:
                red_car_x = -560

        if yellow_car_moving:
            yellow_car_x -= yellow_car_speed * car_factor
            if yellow_car_x < -560:
                yellow_car_x = 520

    dynamic_pen.clear()
    light_pen.clear()
    draw_sun_or_moon()
    draw_stars()
    draw_rainy_atmosphere()

    # Clouds remain in the upper sky and are drawn behind the flag.
    draw_clouds()
    draw_flag()
    draw_birds()
    draw_cars()

    # Dedicated light layer: changing lights no longer redraw/perturb
    # clouds, cars, birds, or the moon.
    draw_lamp_glow(-360)
    draw_lamp_glow(360)
    draw_parliament_lamp_glow(-145, -2)
    draw_parliament_lamp_glow(145, -2)
    draw_rain()
    update_lightning()
    screen.update()
    screen.ontimer(update, 16)

def draw_static_scene():
    """Redraw all non-moving objects for the current day/night mode."""
    global static_scene_night_level
    static_scene_night_level = night_level
    static_pen.clear()
    draw_ground_and_road()
    draw_tree_line()

    # Side trees
    draw_tree(-470, 70, 0.9, 1.3)
    draw_tree(-405, 72, 0.45, 1.3)
    draw_tree(405, 72, 0.45, 1.3)
    draw_tree(470, 70, 0.9, 1.3)
    draw_parliament()
    draw_fence()

    # Large lamp posts
    draw_lamp_post(-360)
    draw_lamp_post(360)

# -----------------------------
# CONTROLS
# -----------------------------
def set_day():
    global is_night, sunset_transition, sunset_step, night_level, moon_rising, moon_step
    global morning_transition, morning_step
    global light_level, light_rising, light_step, car_light_level

    # Can't switch to day while it's raining at night. Rain must be turned
    # off (press B) first.
    if is_night and rain_on:
        return

    # When called from night, play moonset -> dawn -> morning -> noon.
    if is_night:
        sunset_transition = False
        sunset_step = 0
        moon_rising = False
        moon_step = MOON_STEPS
        morning_transition = True
        morning_step = 0

        # Keep the scene visually night-coloured at the first dawn frame,
        # but use the custom transition to draw the descending moon.
        is_night = False
        night_level = 1.0
        light_rising = False
        light_step = 0
        # The static layer already shows full night (nothing has changed
        # yet), so skip redrawing it here - repainting it right on keypress
        # was causing a visible stutter/hitch the instant D was pressed.
        # The transition's own checkpoints will repaint it as it progresses.
        return

    # During sunset, D cancels it and returns directly to daytime.
    morning_transition = False
    morning_step = 0
    sunset_transition = False
    sunset_step = 0
    is_night = False
    night_level = 0.0
    light_level = 0.0
    car_light_level = 0.0
    light_rising = False
    light_step = 0
    moon_rising = False
    moon_step = 0
    screen.bgcolor("#66899B" if rain_on else "#2FA7EA")
    draw_static_scene()

def set_night():
    global is_night, sunset_transition, sunset_step, night_level, moon_rising, moon_step
    global light_level, light_rising, light_step
    global rain_on

    if is_night or sunset_transition:
        return  # already night, or already transitioning
    # Can't switch to night while it's raining in the day. Rain must be
    # turned off (press B) first.
    if rain_on:
        return
    # Play the sunset animation; update() will flip is_night once it finishes.
    sunset_transition = True
    sunset_step = 0
def toggle_pause():
    global paused
    paused = not paused

def toggle_clouds():
    global clouds_moving
    clouds_moving = not clouds_moving

def toggle_birds():
    global birds_moving
    birds_moving = not birds_moving

def toggle_red_car():
    global red_car_moving
    red_car_moving = not red_car_moving

def move_red_left():
    global red_car_x
    red_car_x -= 18

def move_red_right():
    global red_car_x
    red_car_x += 18

def red_speed_up():
    global red_car_speed
    red_car_speed = min(red_car_speed + 0.5, 10.0)

def red_speed_down():
    global red_car_speed
    red_car_speed = max(red_car_speed - 0.5, 0.0)

def toggle_yellow_car():
    global yellow_car_moving
    yellow_car_moving = not yellow_car_moving

def move_yellow_left():
    global yellow_car_x
    yellow_car_x -= 18

def move_yellow_right():
    global yellow_car_x
    yellow_car_x += 18

def yellow_speed_up():
    global yellow_car_speed
    yellow_car_speed = min(yellow_car_speed + 0.5, 10.0)

def yellow_speed_down():
    global yellow_car_speed
    yellow_car_speed = max(yellow_car_speed - 0.5, 0.0)

def bird_speed_up():
    global bird_speed
    bird_speed = min(bird_speed + 0.3, 8.0)

def bird_speed_down():
    global bird_speed
    bird_speed = max(bird_speed - 0.3, 0.2)

def cloud_speed_up():
    global cloud_speed
    cloud_speed = min(cloud_speed + 0.2, 5.0)

def cloud_speed_down():
    global cloud_speed
    cloud_speed = max(cloud_speed - 0.2, 0.1)

def wind_speed_up():
    """Increase wind speed when rain is not active."""
    global wind_speed
    if not rain_on:
        wind_speed = min(wind_speed + 0.4, 5.0)

def wind_speed_down():
    """Decrease wind speed when rain is not active."""
    global wind_speed
    if not rain_on:
        wind_speed = max(wind_speed - 0.4, 0.2)

def reset():
    global is_night, paused, clouds_moving, birds_moving
    global red_car_moving, yellow_car_moving
    global rain_on, rain_on_day, rain_on_night, thunder_on
    global lightning_visible, lightning_timer, next_lightning
    global cloud_x, bird_x, red_car_x, yellow_car_x, wave_time
    global red_car_speed, yellow_car_speed
    global bird_speed, cloud_speed, wind_speed
    global sunset_transition, sunset_step, night_level, static_scene_night_level, moon_rising, moon_step
    global morning_transition, morning_step
    global light_level, light_rising, light_step, car_light_level

    morning_transition = False
    morning_step = 0
    sunset_transition = False
    sunset_step = 0
    is_night = False
    paused = False
    clouds_moving = True
    birds_moving = True
    red_car_moving = True
    yellow_car_moving = True
    rain_on = False
    rain_on_day = False
    rain_on_night = False
    thunder_on = True
    rain_pen.clear()
    lightning_pen.clear()
    lightning_visible = False
    lightning_timer = 0
    next_lightning = 45

    cloud_x = -500
    bird_x = -250
    red_car_x = -520
    yellow_car_x = 430

    wave_time = 0.0
    red_car_speed = 2.2
    yellow_car_speed = 2.2
    bird_speed = 1.0
    cloud_speed = 0.8
    wind_speed = 1.0
    light_level = 0.0
    car_light_level = 0.0
    light_rising = False
    light_step = 0
    night_level = 0.0
    static_scene_night_level = 0.0
    moon_rising = False
    moon_step = 0

    screen.bgcolor("#2FA7EA")

# -----------------------------
# START
# -----------------------------

draw_static_scene()

screen.listen()
screen.onkey(set_day, "d")
screen.onkey(set_day, "D")
screen.onkey(set_night, "n")
screen.onkey(set_night, "N")
screen.onkey(toggle_pause, "p")
screen.onkey(toggle_pause, "P")
screen.onkey(toggle_clouds, "c")
screen.onkey(toggle_clouds, "C")
screen.onkey(toggle_birds, "g")
screen.onkey(toggle_birds, "G")
screen.onkey(toggle_rain, "b")
screen.onkey(toggle_rain, "B")

# Red car controls
screen.onkey(toggle_red_car, "space")
screen.onkey(move_red_left, "Left")
screen.onkey(move_red_right, "Right")
screen.onkey(red_speed_up, "Up")
screen.onkey(red_speed_down, "Down")

# Yellow car controls
screen.onkey(toggle_yellow_car, "k")
screen.onkey(toggle_yellow_car, "K")
screen.onkey(move_yellow_left, "j")
screen.onkey(move_yellow_left, "J")
screen.onkey(move_yellow_right, "l")
screen.onkey(move_yellow_right, "L")
screen.onkey(yellow_speed_down, "u")
screen.onkey(yellow_speed_down, "U")
screen.onkey(yellow_speed_up, "o")
screen.onkey(yellow_speed_up, "O")

# Bird speed controls
screen.onkey(bird_speed_up, "w")
screen.onkey(bird_speed_up, "W")
screen.onkey(bird_speed_down, "s")
screen.onkey(bird_speed_down, "S")

# Cloud speed controls
screen.onkey(cloud_speed_up, "e")
screen.onkey(cloud_speed_up, "E")
screen.onkey(cloud_speed_down, "q")
screen.onkey(cloud_speed_down, "Q")

# Wind speed controls (active when rain is off)
screen.onkey(wind_speed_up, "x")
screen.onkey(wind_speed_up, "X")
screen.onkey(wind_speed_down, "z")
screen.onkey(wind_speed_down, "Z")
screen.onkey(reset, "r")
screen.onkey(reset, "R")
screen.onkey(screen.bye, "Escape")

update()
screen.mainloop()
