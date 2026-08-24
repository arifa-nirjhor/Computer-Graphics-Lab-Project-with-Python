# 🇧🇩 Bangladesh National Parliament — Interactive Turtle Graphics

An interactive **Computer Graphics project built with Python Turtle Graphics**, featuring the **Bangladesh National Parliament** with animated vehicles, environmental effects, weather simulation, day/night transitions, and keyboard interaction.


## ✨ Features

### 🏛️ Graphical Environment

* Bangladesh National Parliament building
* Road, green field, trees, and fence
* Stairs, windows, entrance, and lamp posts
* Animated Bangladesh flag

### 🌤️ Day & Night System

* Day and Night modes
* Smooth sunset and sunrise transitions
* Animated sun and moon
* Gradual sky color changes
* Stars and automatic night lighting
* Vehicle headlights at night

### 🌧️ Weather Effects

* Animated rain
* Storm clouds
* Random lightning
* Mist and rainy atmosphere
* Independent day/night rain states

### 🚗 Vehicle Animation

* Red and yellow cars with independent movement
* Manual movement controls
* Adjustable vehicle speed
* Automatic headlights at night

### ☁️ Environmental Animation

* Moving clouds and birds
* Adjustable cloud and bird speed
* Wind-controlled flag animation
* Pause/resume functionality


## 🎮 Controls

| Key     | Action                     |
| ------- | -------------------------- |
| `D`     | Day Mode                   |
| `N`     | Night Mode                 |
| `P`     | Pause / Resume             |
| `C`     | Start / Stop Clouds        |
| `G`     | Start / Stop Birds         |
| `B`     | Toggle Rain & Storm        |
| `W / S` | Bird Speed Up / Down       |
| `E / Q` | Cloud Speed Up / Down      |
| `X / Z` | Wind Speed Up / Down       |
| `Space` | Start / Stop Red Car       |
| `← / →` | Move Red Car               |
| `↑ / ↓` | Red Car Speed              |
| `K`     | Start / Stop Yellow Car    |
| `J / L` | Move Yellow Car            |
| `U / O` | Yellow Car Speed Down / Up |
| `R`     | Reset                      |
| `Esc`   | Exit                       |


## 🎨 Computer Graphics Concepts

The project demonstrates:

* **2D geometric primitives** — lines, rectangles, circles, and polygons
* **Procedural graphics** for trees, clouds, rain, and other objects
* **Animation** using continuous screen updates
* **Layered rendering** using separate Turtle objects
* **Color interpolation** for day/night transitions
* **Mathematical animation** using sine functions
* **Randomization** for rain and lightning effects
* **Keyboard-based interaction**


## 🏗️ Project Structure

```text
Bangladesh-National-Parliament-Turtle/
│
├── Bangladesh National Parliament.py
└── README.md
```

The main Python file contains the complete scene, animation system, environmental effects, and keyboard controls.


## 🌅 Environment Transitions

### Day → Night

```text
Day → Sunset → Dusk → Night
```

The sky, clouds, sun, environment colors, stars, lamps, and vehicle headlights transition gradually.

### Night → Day

```text
Night → Dawn → Sunrise → Morning → Noon
```

The moon fades, the sun rises, the sky brightens, and night lighting gradually turns off.

---

## 🌧️ Rain & Storm System

The weather system combines:

```text
Rain
 ├── Rain Drops
 ├── Storm Clouds
 ├── Mist
 └── Lightning
```

Rain and lightning are dynamically generated, with separate remembered rain states for day and night.


## 🛠️ Technologies

| Technology          | Purpose                  |
| ------------------- | ------------------------ |
| **Python**          | Programming language     |
| **Turtle Graphics** | 2D graphics & animation  |
| **Math**            | Mathematical animation   |
| **Random**          | Rain & lightning effects |


## 🎯 Project Objectives

1. Create a real-world graphical environment using Python Turtle.
2. Apply fundamental 2D Computer Graphics concepts.
3. Implement interactive animation and keyboard controls.
4. Simulate day/night and weather conditions.
5. Apply mathematical and procedural techniques to graphical animation.


## 🔄 Animation Flow

```text
Initialize Scene
       ↓
Draw Static Environment
       ↓
Update Animation States
       ↓
Move Cars / Birds / Clouds
       ↓
Update Weather & Lighting
       ↓
Redraw Dynamic Layers
       ↓
Screen Update
       ↺
```

## 📚 Academic Purpose

This project was developed for a **Computer Graphics Laboratory** to demonstrate practical applications of **2D graphics, animation, procedural drawing, mathematical modeling, environmental simulation, and user interaction** using Python Turtle Graphics.


## 📄 License

This project is intended for **academic and educational purposes**. The source code may be studied and modified for learning purposes.
