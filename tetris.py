from gturtle import *
import random

# Tetris Formen bestimmen
SHAPES = {
    0: [(-2,0), (-1,0), (0,0), (1,0)],  # I
    1: [(-1,0), (-1,1), (0,0), (1,0)],  # J
    2: [(-1,0), (0,0), (1,0), (1,1)],   # L
    3: [(0,0), (0,1), (1,0), (1,1)],    # O
    4: [(-1,0), (0,0), (0,1), (1,1)],   # S
    5: [(-1,0), (0,0), (0,1), (1,0)],   # T
    6: [(-1,1), (0,1), (0,0), (1,0)]    # Z
}

# Den Tetris Formen eine Farbe zuordnen
COLORS = {
    0: "cyan",
    1: "blue",
    2: "orange",
    3: "yellow",
    4: "green",
    5: "purple",
    6: "red"
}

# Konstanten für das Spielfeld
CELL_SIZE = 50
MAX_COLS = 10
MAX_ROWS = 20
SPAWN_ROWS = 2
SCREEN_WIDTH = MAX_COLS * CELL_SIZE + 200
SCREEN_HEIGHT = (MAX_ROWS + SPAWN_ROWS) * CELL_SIZE

game_started = False

# Event Handler für Mausklicks
def onMousePressed(e):
    global game_started
    
    if not game_started:
        mouse_x = e.getX() - SCREEN_WIDTH / 2
        mouse_y =  SCREEN_HEIGHT / 2 - e.getY()
        
        button_x = -60
        button_y = -40
        button_width = 80
        button_height = 30
        
        # Spiel starten wenn Play gedrückt wird
        if (button_x <= mouse_x <= button_x + button_width and 
            button_y <= mouse_y <= button_y + button_height):
            game_started = True
            
    # Block drehen wenn Spiel läuft und Maus geklickt wird
    elif game.is_running:
        game.rotate_block()
        game.redraw()
    
# Event Handler für Tastatureingaben
def onKeyPressed(e):
    # Spiel Pausieren wenn Esc gedrückt wird
    if e.getKeyCode() == 27:  # ESC key
        game.toggle_pause()
        game.redraw()
        return
    
    # Block mit Pfeiltasten bewegen
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
    
    # Spiel mit Enter neustarten
    if e.getKeyCode() == 10:  # ENTER
        if not game.is_running and game.game_over:
            game.reset()

Options.setPlaygroundSize(SCREEN_WIDTH, SCREEN_HEIGHT)
tf = TurtleFrame(mousePressed = onMousePressed, keyPressed = onKeyPressed)

def grid_to_world_coords(x, y):
    """
    Konvertiert Grid-Koordinaten in Welt-Koordinaten
    
    Das Grid startet bei (0,0) links unten. 
    Die Welt-Koordinaten starten bei (0,0) in der Mitte des Bildschirms.
    
    Args:
        x: X Koordinate im Grid
        y: Y Koordinate im Grid
    
    Returns:
        Tuple: world_x, world_y mit Pixel-Koordinaten
    """
    world_x = (x * CELL_SIZE) + -(SCREEN_WIDTH/2)
    world_y = (y * CELL_SIZE) + -(SCREEN_HEIGHT/2)
    return (world_x, world_y)

class Game():
    """
    Hauptklasse für die Spiel-Logik
    
    Verwaltet:
    - Spielzustand
    - Spielfeld-Grid
    - Score und nächste Formen
    - Kollisionserkennung und Zeilen-Löschung
    """
    def __init__(self):
        """
        Initialisiert ein neues Spiel mit Standardwerten
        """
        self.is_running = True
        self.is_paused = False
        self.game_over = False
        self.score = 0
        self.grid = [[None for y in range(MAX_ROWS + SPAWN_ROWS)] for x in range(MAX_COLS)]
        self.random_bag = []
        self.next_piece_id = None
        
        self.grid_visuals = Grid(tf)
        self.menu = GameMenu(tf)
        self.block = Block(tf, MAX_COLS // 2, MAX_ROWS, self.get_next_piece())
        
    def check_lines(self):
        """
        Prüft ob vollständige Zeilen vorhanden sind und löscht diese
        
        - Geht durch alle Zeilen von unten nach oben
        - Wenn eine Zeile voll ist:  Erhöhe Score, verschiebe Zeilen nach unten
        - Rekursiv aufgerufen um mehrere Zeilen gleichzeitig zu löschen
        """
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
        """
        Gibt die nächste Tetris-Form zurück (7-bag Randomizer)
        
        Das 7-bag System stellt sicher, dass alle 7 Formen
        erscheinen bevor eine wiederholt wird.
        
        Returns:
            Integer: 0-6 der Form-ID
        """
        # Fülle den Beutel falls er leer ist
        if len(self.random_bag) == 0:
            self.random_bag = [0, 1, 2, 3, 4, 5, 6]
            random.shuffle(self.random_bag)
        
        # Verwende die vorher bestimmte nächste Form oder ziehe eine neue falls neu gemischt wurde
        current_piece = self.next_piece_id if self.next_piece_id is not None else self.random_bag.pop()
        self.next_piece_id = self.random_bag.pop()
        return current_piece
    
    def move_block(self, dx, dy):
        """
        Bewegt den aktuellen Block um dx/dy im Grid format
        
        Args:
            dx: Bewegung in x-Richtung (-1 links, 1 rechts, 0 keine) im Grid format
            dy: Bewegung in y-Richtung (-1 runter, 1 hoch, 0 keine) im Grid format
        """
        should_place = self.block.move(dx, dy, self.grid)
        if should_place:
            self.place_block()
    
    def toggle_pause(self):
        """
        Pausiert das Spiel oder setzt es fort
        """
        if not self.game_over:
            self.is_paused = not self.is_paused
            self.is_running = not self.is_paused
        
    def rotate_block(self):
        """
        Rotiert den aktuellen Block um 90° im Uhrzeigersinn
        """
        self.block.rotate()
        
    def place_block(self):
        """
        Platziert den aktuellen Block auf dem Spielfeld
        
        - Speichert Block-Position im Grid
        - Prüft auf Game Over nach dem Platzieren
        - Prüft und löscht vollständige Zeilen nach dem Platzieren
        - Spawnt einen neuen Block
        """
        game_over = self.block.place(self.grid)
        
        if game_over:
            self.is_running = False
            self.game_over = True
            self.redraw()
            return
        
        self.check_lines()
        self.block.reset(self.get_next_piece())
        
    def redraw(self):
        """
        Zeichnet das gesamte Spiel neu
        
        Wird aufgerufen nach jeder Zustandsänderung: 
        - Bewegung des Blocks
        - Rotation
        - Zeilen-Löschung
        - Pause
        - Game Over
        """
        tf.clear()
        
        self.grid_visuals.draw(self.grid)
        self.menu.draw(self.score, self.next_piece_id, self.is_running, self.is_paused, self.game_over)
        if self.is_running or self.is_paused:
            self.block.draw()
                
    def reset(self):
        """
        Setzt das Spiel auf Anfangszustand zurück um es neu zu starten
        """
        self.is_running = True
        self.is_paused = False
        self.game_over = False
        self.score = 0
        self.grid = [[None for y in range(MAX_ROWS + SPAWN_ROWS)] for x in range(MAX_COLS)]
        self.random_bag = []
        self.next_piece_id = None
        self.block = Block(tf, MAX_COLS // 2, MAX_ROWS, self.get_next_piece())
        self.redraw()

class Block(Turtle):
    """
    Repräsentiert einen fallenden Tetris-Block
    
    Verwaltet:
    - Position (px, py)
    - Form (Liste von relativen Koordinaten)
    - Farbe
    - Bewegung und Rotation
    """
    def __init__(self, tf, x, y, shape):
        """
        Initialisiert einen neuen Block
        
        Args: 
            tf: TurtleFrame-Objekt
            x: Start-x-Position im Grid
            y: Start-y-Position im Grid
            shape: Form-ID (0-6)
        """
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
        """
        Zeichnet den Block an seiner aktuellen Position
        
        Iteriert durch alle Positionen der Form und zeichnet
        ein Quadrat an der Stelle
        """
        for dx, dy in self.shape:
            # Konvertiere Gitter-Position zu Welt-Koordinaten
            world_x, world_y = grid_to_world_coords(self.px + dx, self.py + dy)
            
            # Zeichne Quadrat
            self.setPos(world_x, world_y)
            self.setHeading(0)
            self.startPath()
            for i in range(4):
                self.forward(CELL_SIZE)
                self.right(90)
            self.fillPath()

    def move(self, dx, dy, grid):
        """
        Versucht den Block zu bewegen
        
        Prüft Kollisionen mit: 
        - Spielfeld-Rändern
        - Bereits platzierten Blöcken
        - Boden
        
        Args:
            dx:  Bewegung in x-Richtung im Grid Format
            dy: Bewegung in y-Richtung im Grid Format
            grid: Das Spielfeld-Gitter
            
        Returns:
            Boolean: True wenn Block platziert werden soll, ansonsten False
        """
        # Prüft für jede Zelle der Form Kollision
        for shape_x, shape_y in self.shape:
            target_grid_x = self.px + shape_x + dx
            target_grid_y = self.py + shape_y + dy

            # Prüft Horizontale Grenzen
            if target_grid_x < 0 or target_grid_x >= MAX_COLS:
                return False
            # Prüft ob Boden erreicht
            if target_grid_y < 0:
                # Platziere Block
                return True
            # Prüft ob Zelle bereits belegt ist
            if grid[target_grid_x][target_grid_y] is not None:
                if dy != 0:
                    # Wenn darunter bereits belegt ist platziere Block
                    return True
                return False
            
        # Block wird nach gültigen Checks bewegt
        self.px += dx
        self.py += dy
        return False
        
    def rotate(self):
        """
        Rotiert den Block um 90° im Uhrzeigersinn
        
        Verwendet Rotationsmatrix:  (x, y) -> (y, -x)
        Spezielle Offsets für I-Block und O-Block für korrekte Rotation
        """
        offset = 0
        if self.shape_id == 3:      # Offset für O-Block
            offset = 1
        elif self.shape_id == 0:    # Offset für I-Block
            offset = -1
            
        # Überschreibt alte Form mit neuer Rotation
        self.shape = [(y, -x + offset) for (x, y) in self.shape]
        
    def place(self, grid):
        """
        Platziert den Block dauerhaft im Spielfeld
        
        Trägt die Farb-ID des Blocks in das Grid ein
        und prüft ob Game Over eintritt
        
        Args: 
            grid: Das Spielfeld-Grid
            
        Returns:
            Boolean: True wenn Game Over (Block über MAX_ROWS), ansonsten False
        """
        game_over = False
        for shape_x, shape_y in self.shape:
            grid_x = self.px + shape_x
            grid_y = self.py + shape_y
            grid[grid_x][grid_y] = self.color_id # Speicher Block mit Farbe permanent im Grid
            
            # Prüfe ob Block außerhalb des Spielfeldes ist -> Game Over
            if grid_y + 1 > MAX_ROWS:
                game_over = True
                
        return game_over
        
    def reset(self, shape_id):
        """
        Setzt den Block zurück für neuen Block nach der Platzierung
        
        Args:
            shape_id: Die ID der neuen Form (0-6)
        """
        self.px = MAX_COLS // 2
        self.py = MAX_ROWS
        self.shape_id = shape_id
        self.shape = SHAPES[shape_id]
        self.color_id = shape_id
        self.setFillColor(COLORS[self.color_id])

class Grid(Turtle):
    """
    Zeichnet das Spielfeld-Grid und platzierte Blöcke
    """
    def __init__(self, tf):
        """
        Initialisiert das Grid-Zeichenobjekt
        
        Args: 
            tf: TurtleFrame-Objekt
        """
        Turtle.__init__(self, tf)
        self.hideTurtle()
        self.setPenColor("black")
        self.speed(-1)
        
    def draw(self, grid):
        """
        Zeichnet das Spielfeld
        
        1. Zeichnet Grid-Outline an jeder Ecke
        2. Zeichnet alle bereits platzierten Blöcke
        
        Args:
            grid: Das Spielfeld-Grid (2D-Array)
        """
        start_x = -((SCREEN_WIDTH/2))
        start_y = -((SCREEN_HEIGHT/2))
        
        # Zeichne Grid Outline
        for row in range(MAX_ROWS + 1):
            for column in range(MAX_COLS + 1):
                x = start_x + (column * CELL_SIZE)
                y = start_y + (row * CELL_SIZE)
                self.setPos(x, y)
                self.dot(5)
                
        # Zeichne alle platzierten Blöcke
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
    """
    Zeichnet das Spiel-Menü auf der rechten Seite
    
    Zeigt: 
    - Score
    - Vorschau des nächsten Blockes
    - Pausiert, Game Over
    """
    def __init__(self, tf):
        """
        Initialisiert das Menü-Zeichenobjekt
        
        Args: 
            tf: TurtleFrame-Objekt
        """
        Turtle.__init__(self, tf)
        self.hideTurtle()
        self.setPenColor("black")
        self.speed(-1)
        
    def draw(self, score, next_piece_id, is_running, is_paused, game_over):
        """
        Zeichnet das komplette Menü
        
        Args:
            score: Aktuelle Punktzahl
            next_piece_id: ID der nächsten Form (0-6)
            is_running: Läuft das Spiel?
            is_paused: Ist das Spiel pausiert?
            game_over: Ist das Spiel vorbei?
        """
        # Zeichne Score
        self.setPos(SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 4)
        self.label("Score: " + str(score))
        
        # Zeichne Vorschau Text
        self.setPos(SCREEN_WIDTH / 2 - 160, SCREEN_HEIGHT / 6)
        self.label("Next piece:")
        
        # Zeichne Vorschau des nächsten Blockes
        if next_piece_id is not None:
            preview_shape = SHAPES[next_piece_id]
            preview_color = COLORS[next_piece_id]
            self.setFillColor(preview_color)
            
            # Kleinerer Block für Vorschau
            preview_scale = 25
            preview_center_x = SCREEN_WIDTH / 2 - 125
            preview_center_y = SCREEN_HEIGHT / 6 - 100
            
            # Zeichne jede Zelle der Form
            for dx, dy in preview_shape:
                x = preview_center_x + (dx * preview_scale)
                y = preview_center_y + (dy * preview_scale)
                self.setPos(x, y)
                self.startPath()
                for i in range(4):
                    self.forward(preview_scale)
                    self.right(90)
                self.fillPath()
        
        # Zeichne Pause-Meldung
        if is_paused:
            self.setPos(SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 3)
            self.label("PAUSED")
            self.setPos(SCREEN_WIDTH / 2 - 190, SCREEN_HEIGHT / 3 - 30)
            self.label("ESC to resume")
        # Zeichne Game Over-Meldung
        elif game_over:
            self.setPos(SCREEN_WIDTH / 2 - 170, SCREEN_HEIGHT / 3)
            self.label("Game Over!")
            self.setPos(SCREEN_WIDTH / 2 - 190, SCREEN_HEIGHT / 3 - 30)
            self.label("ENTER to restart")

class StartMenu(Turtle):
    """
    Zeichnet das Start-Menü vor Spielbeginn
    
    Zeigt:
    - Titel
    - Play Knopf
    """
    def __init__(self, tf):
        """
        Initialisiert das Startmenü-Zeichenobjekt
        
        Args: 
            tf: TurtleFrame-Objekt
        """
        Turtle.__init__(self, tf)
        self.hideTurtle()
        self.setPenColor("black")
        self.speed(-1)
        
    def draw(self):
        """
        Zeichnet das komplette Startmenü
        """
        # Zeichne Titel
        self.setPos(-60, 100)
        self.label("TETRIS")
        
        # Zeichne Play Knopf
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

# HAUPTPROGRAMM

# Zeige Startmenü und wartet auf Spielbeginn
start_menu = StartMenu(tf)
start_menu.draw()

while not game_started:
    delay(100)
tf.clear()
    
# Initialisiert das Spiel
game = Game()
    
# Main Loop
while True:
    if not game.is_running:
        continue
    game.redraw()
    delay(500)
    game.move_block(0, -1)