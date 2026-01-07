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
    1: "blue",
    2: "orange",
    3: "yellow",
    4: "green",
    5: "purple",
    6: "red"
}

CELL_SIZE = 50
MAX_COLS = 10
MAX_ROWS = 20
SPAWN_ROWS = 2
SCREEN_WIDTH = MAX_COLS * CELL_SIZE + 200
SCREEN_HEIGHT = (MAX_ROWS + SPAWN_ROWS) * CELL_SIZE

is_running = True
score = 0
grid = [[None for y in range(MAX_ROWS + SPAWN_ROWS)] for x in range(MAX_COLS)]
random_bag = []
next_piece_id = None

def onMousePressed(e):
    if is_running:
        block.rotate()
        redraw()
    
def onKeyPressed(e):
    global is_running
    
    if is_running:
        if e.getKeyCode() == e.VK_RIGHT:
            block.move(1, 0)
        elif e.getKeyCode() == e.VK_LEFT:
            block.move(-1, 0)
        elif e.getKeyCode() == e.VK_UP:
            block.rotate()
        elif e.getKeyCode() == e.VK_DOWN:
            block.move(0, -1)
        redraw()
    
    if e.getKeyCode() == 10:  # ENTER
        if not is_running:
            reset_game()

tf = TurtleFrame(mousePressed = onMousePressed, keyPressed = onKeyPressed)
Options.setPlaygroundSize(SCREEN_WIDTH, SCREEN_HEIGHT)

def grid_to_world_coords(x, y):
    world_x = (x * CELL_SIZE) + -(SCREEN_WIDTH/2)
    world_y = (y * CELL_SIZE) + -(SCREEN_HEIGHT/2)
    return (world_x, world_y)

def get_next_piece():
    global random_bag, next_piece_id
    if len(random_bag) == 0:
        random_bag = [0, 1, 2, 3, 4, 5, 6]
        random.shuffle(random_bag)
    
    current_piece = next_piece_id if next_piece_id is not None else random_bag.pop()
    next_piece_id = random_bag.pop()
    return current_piece

def check_lines():
    global score
    for y in range(MAX_ROWS + 1):
        is_full = True
        for x in range(MAX_COLS):
            if grid[x][y] is None:
                is_full = False
                break
            
        if is_full:
            score += 1
            
            for row_above in range(y, MAX_ROWS + 1):
                for x in range(MAX_COLS):
                    grid[x][row_above] = grid[x][row_above + 1]
            for x in range(MAX_COLS):
                grid[x][MAX_ROWS + 1] = None
            
            check_lines()

def reset_game():
    global is_running, score, grid, random_bag, block, next_piece_id
    
    is_running = True
    score = 0
    grid = [[None for y in range(MAX_ROWS + SPAWN_ROWS)] for x in range(MAX_COLS)]
    random_bag = []
    next_piece_id = None
    
    block.clear_all()
    
    block = Block(tf, MAX_COLS // 2, MAX_ROWS, get_next_piece())
    
    redraw()

class Block(Turtle):
    def __init__(self, tf, x, y, shape):
        Turtle.__init__(self, tf)
        self.hideTurtle()
        self.setPenColor("black")
        self.speed(-1)
        self.px, self.py = x, y
        self.shape = SHAPES[shape]
        self.shape_id = shape
        self.color_id = shape
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
        for shape_x, shape_y in self.shape:
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
        global block, is_running
        
        for shape_x, shape_y in self.shape:
            grid_x = self.px + shape_x
            grid_y = self.py + shape_y
            grid[grid_x][grid_y] = self.color_id
            
            if grid_y + 1 > MAX_ROWS:
                is_running = False
                redraw()
                
        if not is_running:
            return
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
            for y in range(MAX_ROWS + SPAWN_ROWS):
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
                    
class GameMenu(Turtle):
    def __init__(self, tf):
        Turtle.__init__(self, tf)
        self.hideTurtle()
        self.setPenColor("black")
        self.speed(-1)
        
    def draw(self):
        self.setPos(SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 4)
        self.label("Score: " + str(score))
        
        self.setPos(SCREEN_WIDTH / 2 - 160, SCREEN_HEIGHT / 6)
        self.label("Next piece:")
        
        if next_piece_id is not None:
            preview_shape = SHAPES[next_piece_id]
            preview_color = COLORS[next_piece_id]
            self.setFillColor(preview_color)
            
            preview_scale = 25
            preview_center_x = SCREEN_WIDTH / 2 - 125
            preview_center_y = SCREEN_HEIGHT / 6 - 100
            
            for dx, dy in preview_shape: 
                x = preview_center_x + (dx * preview_scale)
                y = preview_center_y + (dy * preview_scale)
                
                self.setPos(x, y)
                self.startPath()
                for i in range(4):
                    self.forward(preview_scale)
                    self.right(90)
                self.fillPath()
        
        if is_running == False:
            self.setPos(SCREEN_WIDTH / 2 - 170, SCREEN_HEIGHT / 3)
            self.label("Game Over!")
            self.setPos(SCREEN_WIDTH / 2 - 190, SCREEN_HEIGHT / 3 - 30)
            self.label("ENTER to restart")
        
def redraw():
    block.clear_all()
    
    grid_visuals.draw()
    if is_running: 
        block.draw()
    game_menu.draw()
    
grid_visuals = Grid(tf)
block = Block(tf, MAX_COLS // 2, MAX_ROWS, get_next_piece())
game_menu = GameMenu(tf)
    
while True:
    if not is_running:
        continue
    redraw()
    delay(500)
    block.move(0, -1)