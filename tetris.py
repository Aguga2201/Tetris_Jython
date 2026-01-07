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
SCREEN_WIDTH = MAX_COLS * CELL_SIZE
SCREEN_HEIGHT = (MAX_ROWS + 2) * CELL_SIZE

is_running = True
grid = [[None for y in range(MAX_ROWS + 2)] for x in range(MAX_COLS)]
random_bag = []

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
    elif e.getKeyCode() == e.VK_DOWN:
        block.move(0, -1)
        
    redraw()

tf = TurtleFrame(mousePressed = onMousePressed, keyPressed = onKeyPressed)
Options.setPlaygroundSize(SCREEN_WIDTH, SCREEN_HEIGHT)

def grid_to_world_coords(x, y):
    world_x = (x * CELL_SIZE) + -(SCREEN_WIDTH/2)
    world_y = (y * CELL_SIZE) + -(SCREEN_HEIGHT/2)
    return (world_x, world_y)

def get_next_piece():
    global random_bag
    if len(random_bag) == 0:
        bag = [0, 1, 2, 3, 4, 5, 6]
        random.shuffle(bag)
    return bag.pop()

def check_lines():
    for y in range(MAX_ROWS + 1):
        is_full = True
        for x in range(MAX_COLS):
            if grid[x][y] is None:
                is_full = False
                break
            
        if is_full:
            for row_above in range(y, MAX_ROWS + 1):
                for x in range(MAX_COLS):
                    grid[x][row_above] = grid[x][row_above + 1]
            for x in range(MAX_COLS):
                grid[x][MAX_ROWS + 1] = None
            
            check_lines()

class Block(Turtle):
    def __init__(self, tf, x, y, shape):
        Turtle.__init__(self, tf)
        self.hideTurtle()
        self.setPenColor("black")
        self.speed(-1)
        self.px, self.py = x, y
        self.shape = SHAPES[shape]
        self.shape_id = shape
        self.color_id = random.randint(0,6)
        self.setFillColor(COLORS[self.color_id])

    def draw(self):
        for dx, dy in self.shape:
            world_x, world_y = grid_to_world_coords(self.px + dx, self.py + dy)
            self.setPos(world_x, world_y)
            self.setHeading(0)
            self.startPath()
            for i in range(4):
                self.forward(CELL_SIZE)
                self.right(90)
            self.fillPath()

    def move(self, dx, dy):
        for shape_x, shape_y in self. shape:
            target_grid_x = self.px + shape_x + dx
            target_grid_y = self.py + shape_y + dy

            if target_grid_x < 0 or target_grid_x >= MAX_COLS: 
                return
            if target_grid_y < 0:
                self.place()
                return
            if grid[target_grid_x][target_grid_y] is not None:
                if dy != 0:
                    self.place()
                return
        self.px += dx
        self.py += dy
        
    def rotate(self):
        offset = 0
        if self.shape_id == 3:
            offset = 1
        elif self.shape_id == 0:
            offset = -1
            
        self.shape = [(y, -x + offset) for (x, y) in self.shape]
        
    def place(self):
        global block
        
        for shape_x, shape_y in self.shape:
            grid_x = self.px + shape_x
            grid_y = self.py + shape_y
            grid[grid_x][grid_y] = self.color_id
            
        check_lines()
        block = Block(tf, MAX_COLS // 2, MAX_ROWS, get_next_piece())
        
    def clear_all(self):
        block.clear()
        
class Grid(Turtle):
    def __init__(self, tf):
        Turtle.__init__(self, tf)
        self.hideTurtle()
        self.setPenColor("black")
        self.speed(-1)
        
    def draw(self):
        start_x = -((SCREEN_WIDTH/2))
        start_y = -((SCREEN_HEIGHT/2))
        
        for row in range(MAX_ROWS + 1):
            for collumn in range(MAX_COLS + 1):
                x = start_x + (collumn * CELL_SIZE)
                y = start_y + (row * CELL_SIZE)
            
                self.setPos(x, y)
                self.dot(5)
                
        for x in range(MAX_COLS):
            for y in range(MAX_ROWS + 2):
                if grid[x][y] is not None:
                    self.setFillColor(COLORS[grid[x][y]])
                    world_x, world_y = grid_to_world_coords(x, y)
                    self.setPos(world_x, world_y)
                    self.setHeading(0)
                    self.startPath()
                    for i in range(4):
                        self.forward(CELL_SIZE)
                        self.right(90)
                    self.fillPath()
        
def redraw():
    block.clear_all()
    block.draw()
    grid_visuals.draw()
    
grid_visuals = Grid(tf)
block = Block(tf, MAX_COLS // 2, MAX_ROWS, get_next_piece())
redraw()

while is_running:
    delay(500)
    block.move(0, -1)
    redraw()