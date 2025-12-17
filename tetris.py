from gturtle import *
import random

is_running = True

def onMousePressed(e):
    block.rotate()
    
def onKeyPressed(e):
    print(e.getKeyCode())

    if e.getKeyCode() == e.VK_RIGHT:
        block.move(50, 0)
    elif e.getKeyCode() == e.VK_LEFT:
        block.move(-50, 0)
    elif e.getKeyCode() == e.VK_UP:
        block.rotate()
        
    block.clears()
    block.draw()

tf = TurtleFrame(mousePressed = onMousePressed, keyPressed = onKeyPressed)

SHAPES = {
    0: [(-1.5,0.5), (-0.5,0.5), (0.5,0.5), (1.5,0.5)],      # I
    1: [(-1,0), (-1,1), (0,0), (1,0)],                      # J
    2: [(-1,0), (0,0), (1,0), (1,1)],                       # L
    3: [(-0.5,-0.5), (0.5,-0.5), (0.5,0.5), (-0.5,0.5)],    # O
    4: [(-1,0), (0,0), (0,1), (1,1)],                       # S
    5: [(-1,0), (0,0), (0,1), (1,0)],                       # T
    6: [(-1,1), (0,1), (0,0), (1,0)]                        # Z
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

class Block(Turtle):
    def __init__(self, tf, x, y, shape):
        Turtle.__init__(self, tf)
        self.hideTurtle()
        self.setPenColor("black")
        self.speed(-1)
        self.size = 50
        self.px = x
        self.py = y
        self.shape = SHAPES[shape]
        self.shape_id = shape
        self.setFillColor(COLORS[random.randint(0,6)])

    def draw(self):
        for dx, dy in self.shape:
            self.setPos(self.px + dx * self.size,
                        self.py + dy * self.size)
            self.setHeading(0)
            self.startPath()
            for i in range(4):
                self.forward(self.size)
                self.right(90)
            self.fillPath()

    def move(self, dx, dy):
        self.px += dx
        self.py += dy
        
    def rotate(self):
        ox, oy = 0, 0
        self.shape = [(y - oy, -(x - ox)) for (x, y) in self.shape]
        self.clear()
        self.draw()
        
    def clears(self):
        block.clear()
        
block = Block(tf, 0, 200, 1)
block.draw()

while is_running:
    block.move(0, -50)
    block.clear()
    block.draw()
    delay(500)