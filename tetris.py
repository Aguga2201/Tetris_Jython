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

game_started = False

def onMousePressed(e):
    global game_started
    
    if not game_started:
        mouse_x = e.getX() - SCREEN_WIDTH / 2
        mouse_y =  SCREEN_HEIGHT / 2 - e.getY()
        
        button_x = -60
        button_y = -40
        button_width = 80
        button_height = 30
        
        if (button_x <= mouse_x <= button_x + button_width and 
            button_y <= mouse_y <= button_y + button_height):
            game_started = True
            
    elif game.is_running:
        game.rotate_block()
        game.redraw()
    
def onKeyPressed(e):
    if game.is_running:
        if e.getKeyCode() == e.VK_RIGHT:
            game.move_block(1, 0)
        elif e.getKeyCode() == e.VK_LEFT:
            game.move_block(-1, 0)
        elif e.getKeyCode() == e.VK_UP:
            game.rotate_block()
        elif e.getKeyCode() == e.VK_DOWN:
            game.move_block(0, -1)
        game.redraw()
    
    if e.getKeyCode() == 10:  # ENTER
        if not game.is_running:
            game.reset()

Options.setPlaygroundSize(SCREEN_WIDTH, SCREEN_HEIGHT)
tf = TurtleFrame(mousePressed = onMousePressed, keyPressed = onKeyPressed)

def grid_to_world_coords(x, y):
    world_x = (x * CELL_SIZE) + -(SCREEN_WIDTH/2)
    world_y = (y * CELL_SIZE) + -(SCREEN_HEIGHT/2)
    return (world_x, world_y)

class Game():
    def __init__(self):
        self.is_running = True
        self.score = 0
        self.grid = [[None for y in range(MAX_ROWS + SPAWN_ROWS)] for x in range(MAX_COLS)]
        self.random_bag = []
        self.next_piece_id = None
        
        self.grid_visuals = Grid(tf)
        self.menu = GameMenu(tf)
        self.block = Block(tf, MAX_COLS // 2, MAX_ROWS, self.get_next_piece())
        
    def check_lines(self):
        for y in range(MAX_ROWS):
            is_full = True
            for x in range(MAX_COLS):
                if self.grid[x][y] is None:
                    is_full = False
                    break
                
            if is_full:
                self.score += 1
                for row_above in range(y, MAX_ROWS + 1):
                    for x in range(MAX_COLS):
                        self.grid[x][row_above] = self.grid[x][row_above + 1]
                for x in range(MAX_COLS):
                    self.grid[x][MAX_ROWS + 1] = None
                self.check_lines()
                
    def get_next_piece(self):
        if len(self.random_bag) == 0:
            self.random_bag = [0, 1, 2, 3, 4, 5, 6]
            random.shuffle(self.random_bag)
        
        current_piece = self.next_piece_id if self.next_piece_id is not None else self.random_bag.pop()
        self.next_piece_id = self.random_bag.pop()
        return current_piece
    
    def move_block(self, dx, dy):
        should_place = self.block.move(dx, dy, self.grid)
        if should_place:
            self.place_block()
        
    def rotate_block(self):
        self.block.rotate()
        
    def place_block(self):
        game_over = self.block.place(self.grid)
        
        if game_over:
            self.is_running = False
            self.redraw()
            return
        
        self.check_lines()
        self.block.reset(self.get_next_piece())
        
    def redraw(self):
        tf.clear()
        
        self.grid_visuals.draw(self.grid)
        self.menu.draw(self.score, self.next_piece_id, self.is_running)
        if self.is_running:
            self.block.draw()
                
    def reset(self):
        self.is_running = True
        self.score = 0
        self.grid = [[None for y in range(MAX_ROWS + SPAWN_ROWS)] for x in range(MAX_COLS)]
        self.random_bag = []
        self.next_piece_id = None
        self.block = Block(tf, MAX_COLS // 2, MAX_ROWS, self.get_next_piece())
        self.redraw()

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

    def move(self, dx, dy, grid):
        for shape_x, shape_y in self.shape:
            target_grid_x = self.px + shape_x + dx
            target_grid_y = self.py + shape_y + dy

            if target_grid_x < 0 or target_grid_x >= MAX_COLS:
                return False
            if target_grid_y < 0:
                return True
            if grid[target_grid_x][target_grid_y] is not None:
                if dy != 0:
                    return True
                return False
        self.px += dx
        self.py += dy
        return False
        
    def rotate(self):
        offset = 0
        if self.shape_id == 3:
            offset = 1
        elif self.shape_id == 0:
            offset = -1
            
        self.shape = [(y, -x + offset) for (x, y) in self.shape]
        
    def place(self, grid):
        game_over = False
        for shape_x, shape_y in self.shape:
            grid_x = self.px + shape_x
            grid_y = self.py + shape_y
            grid[grid_x][grid_y] = self.color_id
            
            if grid_y + 1 > MAX_ROWS:
                game_over = True
                
        return game_over
        
    def reset(self, shape_id):
        self.px = MAX_COLS // 2
        self.py = MAX_ROWS
        self.shape_id = shape_id
        self.shape = SHAPES[shape_id]
        self.color_id = shape_id
        self.setFillColor(COLORS[self.color_id])

class Grid(Turtle):
    def __init__(self, tf):
        Turtle.__init__(self, tf)
        self.hideTurtle()
        self.setPenColor("black")
        self.speed(-1)
        
    def draw(self, grid):
        start_x = -((SCREEN_WIDTH/2))
        start_y = -((SCREEN_HEIGHT/2))
        
        for row in range(MAX_ROWS + 1):
            for column in range(MAX_COLS + 1):
                x = start_x + (column * CELL_SIZE)
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
        
    def draw(self, score, next_piece_id, is_running):
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
        
        if not is_running:
            self.setPos(SCREEN_WIDTH / 2 - 170, SCREEN_HEIGHT / 3)
            self.label("Game Over!")
            self.setPos(SCREEN_WIDTH / 2 - 190, SCREEN_HEIGHT / 3 - 30)
            self.label("ENTER to restart")

class StartMenu(Turtle):
    def __init__(self, tf):
        Turtle.__init__(self, tf)
        self.hideTurtle()
        self.setPenColor("black")
        self.speed(-1)
        
    def draw(self):
        self.setPos(-60, 100)
        self.label("TETRIS")
        
        self.setPenColor("black")
        self.setPos(-60, -40)
        self.setHeading(0)
        repeat 2:
            self.forward(30)
            self.right(90)
            self.forward(80)
            self.right(90)
        
        self.setPos(-50, -35)
        self.label("PLAY")

start_menu = StartMenu(tf)
start_menu.draw()

while not game_started:
    delay(100)
tf.clear()
    
game = Game()
    
while True:
    if not game.is_running:
        continue
    game.redraw()
    delay(500)
    game.move_block(0, -1)