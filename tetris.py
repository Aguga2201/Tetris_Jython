from gturtle import *
import random

SHAPES = {
    0: [(-2,0), (-1,0), (0,0), (1,0)],  # I
    1: [(-1,0), (-1,1), (0,0), (1,0)],  # J
    2: [(-1,0), (0,0), (1,0), (1,1)],   # L
    3: [(0,0), (0,1), (1,0), (1,1)],    # O
    4: [(-1,0), (0,0), (0,1), (1,1)],   # S
    5: [(-1,0), (0,0), (0,1), (1,0)],   # T
    6: [(-1,1), (0,1), (0,0), (1,0)]    # Z
}

COLORS = {
    0: "cyan",
    1: "yellow",
    2: "purple",
    3: "green",
    4: "red",
    5: "orange",
    6: "blue"
}

CELL_SIZE = 50
MAX_COLS = 10
MAX_ROWS = 20

is_running = True
grid = [[0 for y in range(MAX_ROWS + 2)] for x in range(MAX_COLS)]
grid[4][0] = 1

def onMousePressed(e):
    block.rotate()
    redraw()
    
def onKeyPressed(e):
    if e.getKeyCode() == e.VK_RIGHT:
        block.move(1, 0)
    elif e.getKeyCode() == e.VK_LEFT:
        block.move(-1, 0)
    elif e.getKeyCode() == e.VK_UP:
        block.rotate()
        
    redraw()

tf = TurtleFrame(mousePressed = onMousePressed, keyPressed = onKeyPressed)
Options.setPlaygroundSize(500, 1100)

def world_to_grid_coords(x, y):
    grid_x = int((x - -250) / CELL_SIZE)
    grid_y = int((y - -550) / CELL_SIZE)
    return (grid_x, grid_y)

def grid_to_world_coords(x, y):
    world_x = (x * CELL_SIZE) + -250
    world_y = (y * CELL_SIZE) + -550
    return (world_x, world_y)

class Block(Turtle):
    def __init__(self, tf, x, y, shape):
        Turtle.__init__(self, tf)
        self.hideTurtle()
        self.setPenColor("black")
        self.speed(-1)
        self.px, self.py = grid_to_world_coords(x, y)
        self.shape = SHAPES[shape]
        self.shape_id = shape
        self.setFillColor(COLORS[random.randint(0,6)])

    def draw(self):
        for dx, dy in self.shape:
            self.setPos(self.px + dx * CELL_SIZE,
                        self.py + dy * CELL_SIZE)
            self.setHeading(0)
            self.startPath()
            for i in range(4):
                self.forward(CELL_SIZE)
                self.right(90)
            self.fillPath()

    def move(self, dx, dy):
        for shape_x, shape_y in self.shape:
            target_world_x = self.px + (shape_x * CELL_SIZE) + (dx * CELL_SIZE)
            target_world_y = self.py + (shape_y * CELL_SIZE) + (dy * CELL_SIZE)
            target_grid_x, target_grid_y = world_to_grid_coords(target_world_x, target_world_y)

            if target_grid_x < 0 or target_grid_x > 9:
                return
            if target_grid_y < 0:
                return
            if grid[target_grid_x][target_grid_y] == 1:
                return
        self.px += dx * CELL_SIZE
        self.py += dy * CELL_SIZE
        
    def rotate(self):
        offset = 0
        if self.shape_id == 3:
            offset = 1
        elif self.shape_id == 0:
            offset = -1
            
        self.shape = [(y, -x + offset) for (x, y) in self.shape]
        
    def clear_all(self):
        block.clear()
        
class Grid(Turtle):
    def __init__(self, tf):
        Turtle.__init__(self, tf)
        self.hideTurtle()
        self.setPenColor("black")
        self.speed(-1)
        
    def draw(self):
        start_x = -(500/2)
        start_y = -(1100/2)
        
        for row in range(MAX_ROWS + 1):
            for collumn in range(MAX_COLS + 1):
                x = start_x + (collumn * CELL_SIZE)
                y = start_y + (row * CELL_SIZE)
            
                self.setPos(x, y)
                self.dot(5)
        
def redraw():
    block.clear_all()
    block.draw()
    grid_visuals.draw()
    
grid_visuals = Grid(tf)
block = Block(tf, 4, 20, 1)
redraw()

while is_running:
    block.move(0, -1)
    redraw()
    delay(500)