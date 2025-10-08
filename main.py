from tkinter import *
import random
import collections

# ---------------- Configuration ----------------
GAME_WIDTH = 600
GAME_HEIGHT = 600
SPACE_SIZE = 20
ROWS = GAME_HEIGHT // SPACE_SIZE
COLS = GAME_WIDTH // SPACE_SIZE
BODY_PARTS = 3
SNAKE_COLOR = "yellow"
FOOD_COLOR = "red"
BACKGROUND_COLOR = "black"

SPEED = 60  # ms entre chaque frame

# Mettre à True si on veut que le serpent traverse les bords (wrap), sinon il évite les bords
WRAP_EDGES = False

# ---------------- État ----------------
score = 0

# ---------------- Cycle Hamiltonien ----------------
def cycle_hamiltonien(rows, cols):
    cycle = []
    for r in range(rows):

        if r % 2 == 0:
            for c in range(cols):
                cycle.append((r, c))
        else:
            for c in reversed(range(cols)):
                cycle.append((r, c))
    return cycle

cycle = cycle_hamiltonien(ROWS, COLS)
pos_to_idx = {cycle[i]: i for i in range(len(cycle))}
pos_to_next = {cycle[i]: cycle[(i+1) % len(cycle)] for i in range(len(cycle))}

# ---------------- Fonctions utilitaires ----------------
def inside_cell(cell):
    r, c = cell
    return 0 <= r < ROWS and 0 <= c < COLS

def body_cells_from_coords(coords):
    """Retourne un set des cellules occupées (r,c) à partir des coordonnées pixel du serpent."""
    return set((y // SPACE_SIZE, x // SPACE_SIZE) for x, y in coords)

# ---------------- Recherche en largeur (BFS) ----------------
def bfs(start, goal, snake_body):
    """Retourne une liste de cellules (r,c) formant un chemin du start au goal en évitant le corps du serpent."""
    q = collections.deque([start])
    prev = {start: None}
    body_set = body_cells_from_coords(snake_body)
    while q:
        r, c = q.popleft()
        if (r, c) == goal:
            path = []
            cur = goal
            while cur is not None:
                path.append(cur)
                cur = prev[cur]
            return list(reversed(path))
        # Ajouter les voisins non visités à la queue
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if (nr, nc) not in prev and ((nr, nc) not in body_set or (nr, nc) == goal):
                    prev[(nr, nc)] = (r, c)
                    q.append((nr, nc))
    return None

# ---------------- Classes Snake et Food ----------------
class Snake:
    def __init__(self):
        self.coordinates = []  
        self.squares = []
        # Initialiser le serpent avec les premières cellules du cycle
        start = cycle[0:BODY_PARTS]
        for (r, c) in reversed(start):  
            x, y = c * SPACE_SIZE, r * SPACE_SIZE
            self.coordinates.append([x, y])
            square = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR, tag="snake")
            self.squares.append(square)

    def head_cell(self):
        x, y = self.coordinates[0]
        
        return (y // SPACE_SIZE, x // SPACE_SIZE)

    def occup_cells(self):
        return body_cells_from_coords(self.coordinates)

class Food:
    def __init__(self):
        while True:
            r = random.randint(0, ROWS - 1)
            c = random.randint(0, COLS - 1)
            coord = [c * SPACE_SIZE, r * SPACE_SIZE]
           
            if coord not in snake.coordinates:
                break
        self.cell = (r, c)
        self.coordinates = [c * SPACE_SIZE, r * SPACE_SIZE]
       
        canvas.create_oval(self.coordinates[0], self.coordinates[1],
                           self.coordinates[0] + SPACE_SIZE, self.coordinates[1] + SPACE_SIZE,
                           fill=FOOD_COLOR, tag="food")

# ---------------- Détection de collision ----------------
def check_collisions(snake):
    head = snake.coordinates[0]
   
    if head in snake.coordinates[1:]:
        return True
   
    hx, hy = head
    if not (0 <= hx < GAME_WIDTH and 0 <= hy < GAME_HEIGHT):
        return True
    return False

# ---------------- BFS et Hamiltonien ----------------
def move_(snake, food):
    head_cell = snake.head_cell()

    
    path = bfs(head_cell, food.cell, snake.coordinates)
    if path and len(path) > 1:
        candidate = path[1]
    else:
       
        candidate = pos_to_next.get(head_cell, None)
        if candidate is None:
            
            for dr,dc in [(0,1),(1,0),(0,-1),(-1,0)]:
                cand = (head_cell[0]+dr, head_cell[1]+dc)
                if inside_cell(cand):
                    candidate = cand
                    break
            if candidate is None:
                candidate = head_cell 

    # Si WRAP_EDGES activé -> appliquer wrap modulo
    if WRAP_EDGES:
        candidate = (candidate[0] % ROWS, candidate[1] % COLS)
        return candidate

    # Si WRAP_EDGES désactivé -> vérifier que candidate est dans la grille
    if not inside_cell(candidate):
        fallback = pos_to_next.get(head_cell)
        if fallback and inside_cell(fallback):
            return fallback
        # Sinon essayer de trouver une cellule voisine libre
        for dr,dc in [(0,1),(1,0),(0,-1),(-1,0)]:
            cand = (head_cell[0]+dr, head_cell[1]+dc)
            if inside_cell(cand):
                
                if not is_cell_occup(cand, snake, allow_tail=True):
                    return cand
        # Si aucune cellule voisine libre, retourner fallback si possible
        if fallback:
            return fallback
        # Sinon rester sur place (perdu)
        return head_cell

    # Vérifier que la cellule candidate n'est pas occupée par le corps du serpent (sauf queue)
    return candidate

def is_cell_occup(cell, snake, allow_tail=False):
    """Vérifie si une cellule (r,c) est occupée par le corps du serpent.
    Si allow_tail est True, la cellule de la queue est ignorée (utile pour le mouvement)."""
    occupied = snake.occup_cells()
    if allow_tail and len(snake.coordinates) > 0:
        tail = snake.coordinates[-1]
        tail_cell = (tail[1] // SPACE_SIZE, tail[0] // SPACE_SIZE)
        occupied.discard(tail_cell)
    return cell in occupied

# ---------------- Tour suivant ----------------
def next_turn(snake, food):
    global score

    head_cell = snake.head_cell()
    next_cell = move_(snake, food)

    # Appliquer wrap si activé
    if WRAP_EDGES:
        new_r = next_cell[0] % ROWS
        new_c = next_cell[1] % COLS
    else:
        new_r, new_c = next_cell

    # Si la cellule n'est pas valide, utiliser le fallback du cycle Hamiltonien
    if not inside_cell((new_r, new_c)):
        fallback = pos_to_next.get(head_cell, head_cell)
        new_r, new_c = fallback

    new_x, new_y = new_c * SPACE_SIZE, new_r * SPACE_SIZE

    # Mettre à jour les coordonnées du serpent
    snake.coordinates.insert(0, [new_x, new_y])
    square = canvas.create_rectangle(new_x, new_y, new_x + SPACE_SIZE, new_y + SPACE_SIZE, fill=SNAKE_COLOR)
    snake.squares.insert(0, square)

    # Vérifier si le serpent a mangé la nourriture
    if (new_r, new_c) == food.cell:
        score += 1
        label.config(text=f"score: {score}")
        canvas.delete("food")
        food = Food()
    else:
        # Retirer la dernière partie du serpent
        del snake.coordinates[-1]
        canvas.delete(snake.squares[-1])
        del snake.squares[-1]

    # Vérifier les collisions
    if check_collisions(snake):
        game_over()
        return

    # Planifier le prochain tour
    window.after(SPEED, next_turn, snake, food)

# ---------------- Fin de partie ----------------
def game_over():
    canvas.delete(ALL)
    canvas.create_text(canvas.winfo_width() / 2, canvas.winfo_height() / 2,
                       font=('consolas', 70), text="GAME OVER", fill="red", tag="gameover")

# ---------------- Configuration de l'interface ----------------
window = Tk()
window.title("Snake Game with Hamiltonian Cycle")
window.resizable(False, False)

label = Label(window, text=f"score: {score}", font=('consolas', 40))
label.pack()

canvas = Canvas(window, bg=BACKGROUND_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
canvas.pack()

window.update()

window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Démarrer le jeu
snake = Snake()
food = Food()
next_turn(snake, food)

window.mainloop()
