from tcod import Color

# Constants
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 43
PANEL_HEIGHT = 7
LIMIT_FPS = 20
MS_PER_UPDATE = 16

MAP_WIDTH = 80
MAP_HEIGHT = 43

BAR_WIDTH = 20

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

color_dark_wall = Color(0, 0, 100)
color_dark_ground = Color(50, 50, 150)

