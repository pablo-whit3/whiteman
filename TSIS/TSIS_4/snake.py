import pygame, sys
from pygame.locals import *
import random
import psycopg2
import json
from config import dbhost, dbpassword, dbname, dbuser

pygame.init()

#подключаю данные о бд
conn = psycopg2.connect(
    host=dbhost,
    database=dbname,
    user=dbuser,
    password=dbpassword
)

#создаю таблицы с игроками и сессиями
def init_db():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            score INTEGER NOT NULL,
            level_reached INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()

cur = conn.cursor()
init_db()

#ввожу постоянные и переменные
WIDTH = 600
HEIGHT = 600
CELL = 30
WHITE = (255,255,255)
BLACK = (0,0,0)
GREY = (200,200,200)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
DARK_RED = (139,0,0)
DARK_BLUE = (0,0,139)
LIGHT_BLUE = (173,216,230)

#сет экрана
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, 700))
pygame.display.set_caption("Snake")

#рендер надписей и шрифты
font=pygame.font.SysFont("Verdana",60)
font_small=pygame.font.SysFont("Verdana", 20)
game_over = font.render("GAME OVER", True, BLACK)

#функции json настройки и парсер цвета
def load_settings():
    try:
        with open("settings.json", "r") as f:
            return json.load(f)
    except:
        return {"sound": True, "grid_overlay": 1, "snake_color": GREEN}

def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f)

def parse_rgb(text):
    try:
        parts = text.split(",")
        if len(parts) != 3:
            return GREEN

        r = int(parts[0].strip())
        g = int(parts[1].strip())
        b = int(parts[2].strip())

        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        return (r, g, b)
    except:
        return GREEN

#загрузка настроек в код
settings = load_settings()

grid_overlay = settings["grid_overlay"]
snake_color = tuple(settings["snake_color"])

#функция для сохранения результатов в бд
def save_score(player_name, SCORE, LEVEL):
    cur.execute("SELECT id FROM players WHERE username=%s", (player_name,))
    player = cur.fetchone()

    if player is None:
        cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (player_name,))
        player_id = cur.fetchone()[0]
    else:
        player_id = player[0]

    cur.execute("""
        INSERT INTO game_sessions (player_id, score, level_reached)
        VALUES (%s, %s, %s)
    """, (player_id, SCORE, LEVEL))

    conn.commit()

#функция для выгрузки результатов из бд
def load_scores():
    cur.execute("""
        SELECT p.username, g.score, g.level_reached, g.played_at
        FROM game_sessions g
        JOIN players p ON p.id = g.player_id
        ORDER BY g.score DESC
        LIMIT 10
    """)
    return cur.fetchall()

#функция для лучшего результата игрока
def get_best_score(player_name):
    cur.execute("""
        SELECT MAX(g.score)
        FROM game_sessions g
        JOIN players p ON p.id = g.player_id
        WHERE p.username = %s
    """, (player_name,))
    return cur.fetchone()[0] or 0

#создаю функцию по ресету игры и обновлению всех переменных
def reset_game():
    global food, snake, poison, buster, obst 
    global FPS, SCORE, LEVEL, FOOD_TO_PASS, active_buster, buster_timer, score_saved, color_input_flag, color_input
    FPS = 5
    SCORE = 0
    LEVEL = 1
    FOOD_TO_PASS = 5
    active_buster = None
    buster_timer = 0
    score_saved = False
    color_input_flag = False
    color_input = ""

    #создаю объекты классов для обращения к ним
    snake = Snake()
    food = Food()
    poison = Poison()
    buster = Buster()
    obst = Obstacles()



#функции для поля
def draw_grid():
    for i in range(HEIGHT // CELL):
        for j in range(WIDTH // CELL):
            pygame.draw.rect(screen, GREY, (i * CELL, j * CELL, CELL, CELL), 1)

def draw_grid_chess():
    colors = [WHITE, GREY]

    for i in range(HEIGHT // CELL):
        for j in range(WIDTH // CELL):
            pygame.draw.rect(screen, colors[(i + j) % 2], (i * CELL, j * CELL, CELL, CELL))

#создаю класс координат
class Point:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.x}, {self.y}"
    
#создаю класс для змейки
class Snake:
    def __init__(self):
        self.body = [Point(10,11), Point(10,12), Point(10,13)]
        self.dx = 1
        self.dy = 0
    def move(self):
        for i in range(len(self.body)-1,0,-1):
            self.body[i].x = self.body[i-1].x
            self.body[i].y = self.body[i-1].y
        
        self.body[0].x += self.dx
        self.body[0].y += self.dy

    #проверяю границы
    def check_wall_collision(self):
        head = self.body[0]
        if (head.x < 0 or head.x >= WIDTH // CELL or
            head.y < 0 or head.y >= HEIGHT // CELL):
            return True
        return False

    #прорисовка    
    def draw(self):
        head = self.body[0]
        pygame.draw.rect(screen, RED, (head.x*CELL, head.y*CELL, CELL, CELL))
        for segment in self.body[1:]:
            pygame.draw.rect(screen, snake_color, (segment.x*CELL, segment.y*CELL, CELL, CELL))

    #подбор еды    
    def check_collision(self,food):
        global SCORE, FPS, LEVEL, FOOD_TO_PASS
        head=self.body[0]
        if head.x == food.pos.x and head.y == food.pos.y:
            gained=food.weight
            print("Got food!")
            SCORE=SCORE + gained
            for _ in range(gained):
                self.body.append(Point(self.body[-1].x, self.body[-1].y))
            food.spawn(snake.body, obst.blocks)
            if SCORE >= FOOD_TO_PASS:
                LEVEL+=1
                FPS+=1
                FOOD_TO_PASS+=5

    #подбор бустеров
    def check_busters(self,buster):
        global FPS, active_buster, buster_timer
        head=self.body[0]
        if head.x == buster.pos.x and head.y == buster.pos.y:
            print(f"Got {buster.type}!")
            if active_buster == buster.type:
                if buster.type in ["nitro", "slower"]:
                    buster_timer = pygame.time.get_ticks()
            else:
                if active_buster == "nitro":
                    FPS -= 3
                elif active_buster == "slower":
                    FPS += 3

                active_buster = buster.type

                if active_buster == "nitro":
                    FPS += 3
                    buster_timer = pygame.time.get_ticks()

                elif active_buster == "slower":
                    FPS = max(2, FPS - 3)
                    buster_timer = pygame.time.get_ticks()

                elif active_buster == "shield":
                    buster_timer = 0

            buster.spawn(self.body, obst.blocks)


    #подбор ядовитой еды
    def check_collision_poison(self,poison):
        global FPS, game_status
        head=self.body[0]
        if head.x == poison.pos.x and head.y == poison.pos.y:
            print("Got poisoned")
            for _ in range(2):
                if len(self.body) > 3:
                    self.body.pop()
                else:
                    game_status = "game_over"
                    break
            poison.spawn(snake.body, obst.blocks)

    #запрет на столкновение с собой
    def check_self_collision(self):
        head = self.body[0]
        for segment in self.body[1:]:
            if head.x == segment.x and head.y == segment.y:
                return True
        return False

    #столкновение с блоками
    def check_obst_collision(self, obst):
        head = self.body[0]
        for o in obst:
            if head.x == o.x and head.y == o.y :
                return True
        return False  

#создаю класс для еды
class Food:
    def __init__(self):
        self.pos = Point(9,9)
        self.weight = random.randint(1, 3)
        self.timer = pygame.time.get_ticks()

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.pos.x*CELL, self.pos.y*CELL, CELL, CELL))

    def spawn(self, snake_body, obst):
        while True:
            self.pos.x = random.randint(0, WIDTH // CELL - 1)
            self.pos.y = random.randint(0, HEIGHT // CELL - 1)

            ok = True
            for s in snake_body:
                if s.x == self.pos.x and s.y == self.pos.y:
                    ok = False
                    break
            for o in obst:
                if o.x == self.pos.x and o.y == self.pos.y:
                    ok = False
                    break

            if ok:
                break
        self.weight = random.randint(1, 3)
        self.timer = pygame.time.get_ticks()
    
    def time_control(self):
        if pygame.time.get_ticks() - self.timer > 8000:
            self.spawn(snake.body, obst.blocks)
            self.timer = pygame.time.get_ticks()

#создаю класс для ядовитой еды
class Poison:
    def __init__(self):
        self.pos = Point(random.randint(1,20), random.randint(1,20))
        self.timer = pygame.time.get_ticks()

    def draw(self):
        pygame.draw.rect(screen, DARK_RED, (self.pos.x*CELL, self.pos.y*CELL, CELL, CELL))

    def spawn(self, snake_body, obst):
        while True:
            self.pos.x = random.randint(0, WIDTH // CELL - 1)
            self.pos.y = random.randint(0, HEIGHT // CELL - 1)

            ok = True
            for s in snake_body:
                if s.x == self.pos.x and s.y == self.pos.y:
                    ok = False
                    break
            for o in obst:
                if o.x == self.pos.x and o.y == self.pos.y:
                    ok = False
                    break

            if ok:
                break
        self.timer = pygame.time.get_ticks()
    
    def time_control(self):
        if pygame.time.get_ticks() - self.timer > 8000:
            self.spawn(snake.body, obst.blocks)
            self.timer = pygame.time.get_ticks()

#создаю бустеры
class Buster:
    def __init__(self):
        super().__init__()
        self.type = random.choice(["nitro", "slower", "shield"])
        self.pos = Point(random.randint(1,20), random.randint(1,20))
        self.timer = pygame.time.get_ticks()

    def spawn(self, snake_body, obst):
        self.type = random.choice(["nitro", "slower", "shield"])
        while True:
            self.pos.x = random.randint(0, WIDTH // CELL - 1)
            self.pos.y = random.randint(0, HEIGHT // CELL - 1)

            ok = True
            for s in snake_body:
                if s.x == self.pos.x and s.y == self.pos.y:
                    ok = False
                    break
            for o in obst:
                if o.x == self.pos.x and o.y == self.pos.y:
                    ok = False
                    break

            if ok:
                break
        self.timer = pygame.time.get_ticks()
    
    def draw(self):
        if self.type == "nitro":
            pygame.draw.rect(screen, BLUE, (self.pos.x*CELL, self.pos.y*CELL, CELL, CELL))
        elif self.type == "slower":
            pygame.draw.rect(screen, DARK_BLUE, (self.pos.x*CELL, self.pos.y*CELL, CELL, CELL))
        else:
            pygame.draw.rect(screen, LIGHT_BLUE, (self.pos.x*CELL, self.pos.y*CELL, CELL, CELL))

    def time_control(self):
        if pygame.time.get_ticks() - self.timer > 8000:
            self.spawn(snake.body, obst.blocks)

#создаю класс для препятствий
class Obstacles:
    def __init__(self):
        self.blocks = []

    def generate(self, LEVEL, snake_body):
        self.blocks = []

        if LEVEL < 3:
            return

        count = 8

        for _ in range(count):
            while True:
                x = random.randint(0, WIDTH // CELL - 1)
                y = random.randint(0, HEIGHT // CELL - 1)

                ok = True

                for s in snake_body:
                    if s.x == x and s.y == y:
                        ok = False

                if ok:
                    self.blocks.append(Point(x, y))
                    break

    def draw(self):
        for o in self.blocks:
            pygame.draw.rect(screen, GREY, (o.x*CELL, o.y*CELL, CELL, CELL))

#гейм луп и евент лупы
running = True
color_input_flag = False
name_input_flag = True
player_name = ""
reset_game()
while running:
    #обязательный ввод имени
    if name_input_flag:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    name_input_flag = False
                    game_status = "menu"
                elif event.key == K_BACKSPACE:
                    player_name = player_name[:-1]
                else :
                    player_name += event.unicode
        screen.fill(BLACK)
        text = font_small.render("Enter username: " + player_name, True, WHITE)
        screen.blit(text, (150, 300))
        pygame.display.flip()
        continue
    
    #подгружаю лучший результат
    best_score = get_best_score(player_name)

    #режим меню
    if game_status == "menu":
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    settings = load_settings()
                    car_color = settings["snake_color"]
                    grid_overlay = settings["grid_overlay"]
                    game_status = "game"
                if event.key == K_s:
                    game_status = "settings"
                if event.key == K_l:
                    game_status = "leaderboard"
                if event.key == K_ESCAPE:
                    running = False
        
        screen.fill(WHITE)
        t1=font_small.render("PRESS SPACE TO START", True, BLACK)
        t2=font_small.render("press s to settings", True, BLACK)
        t3=font_small.render("press l to leaderboard", True, BLACK)
        t4=font_small.render("press esc to quit", True, BLACK)
        screen.blit(t1, (50, 300))
        screen.blit(t2, (50, 350))
        screen.blit(t3, (50, 400))
        screen.blit(t4, (50, 450))
        pygame.display.flip()
        continue

    #режим настроек
    if game_status == "settings":
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    save_settings({"grid_overlay" : grid_overlay, "snake_color": list(snake_color)})
                    game_status = "menu"
                if event.key == K_g:
                    grid_overlay = not grid_overlay

                if event.key == K_SPACE:
                    color_input_flag = True
                elif color_input_flag:
                    if event.key == K_RETURN:
                        snake_color = parse_rgb(color_input)
                        color_input = ""
                        color_input_flag = False
                    elif event.key == K_BACKSPACE:
                        color_input = color_input[:-1]
                    else:
                        color_input += event.unicode
        
        
        screen.fill(WHITE)

        t1=font_small.render("SETTINGS", True, BLACK)
        t3=font_small.render(f"Grid overlay(G): {'ON' if grid_overlay else 'OFF'}", True, BLACK)
        t4=font_small.render(f"Put an RGB color / x,x,x: {color_input}", True, BLACK)
        t6=font_small.render("ESC to save and go back", True, BLACK)
        t8=font_small.render("Space to change, ENTER to save color", True, BLACK)

        screen.blit(t1, (180, 30))
        screen.blit(t3, (100, 250))
        screen.blit(t4, (100, 300))
        screen.blit(t6, (100, 100))
        screen.blit(t8, (100, 350))

        pygame.draw.rect(screen, snake_color, (550, 300, CELL, CELL))
        pygame.display.flip()
        continue
    
    #режим таблицы лидеров
    if game_status == "leaderboard":
        scores = load_scores() or []

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    game_status = "menu"

        screen.fill(WHITE)

        title=font.render("TOP 10", True, BLACK)
        screen.blit(title, (150,50))

        y=150
        for i, s in enumerate(scores):
            t = font_small.render(f"{i+1}. {s[0]} - {s[1]} - lvl {s[2]} - {s[3]}", True, BLACK)
            screen.blit(t, (100, y))
            y+=40
        
        pygame.display.flip()
        continue

    #запуск игры
    if game_status == "game":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    snake.dx = 1
                    snake.dy = 0
                elif event.key == pygame.K_LEFT:
                    snake.dx = -1
                    snake.dy = 0
                elif event.key == pygame.K_DOWN:
                    snake.dx = 0
                    snake.dy = 1
                elif event.key == pygame.K_UP:
                    snake.dx = 0
                    snake.dy = -1

        #отрисовка среды
        screen.fill(BLACK)
        score=font_small.render(f"SCORE:{int(SCORE)}", True, WHITE)
        screen.blit(score, (10,610))
        current_level=font_small.render(f"LEVEL:{str(LEVEL)}", True, WHITE)
        screen.blit(current_level, (320,610))
        best=font_small.render(f"Your best:{best_score}", True, WHITE)
        screen.blit(best, (10, 640))
        if active_buster:
            power_text = font_small.render(f"BUSTER: {active_buster}", True, WHITE)
            screen.blit(power_text, (150, 610))

        #механизмы при игре
        snake.move()
        if grid_overlay:
            draw_grid()
        snake.draw()
        food.time_control()
        food.draw()
        snake.check_collision(food)
        buster.time_control()
        buster.draw()
        snake.check_busters(buster)
        poison.draw()
        snake.check_collision_poison(poison)
        poison.time_control()
        if LEVEL >= 3 and len(obst.blocks) == 0:
            obst.generate(LEVEL, snake.body)
        obst.draw()
        #проверка на столкновения с щитом и без
        if active_buster == "shield":
            if snake.check_wall_collision() or snake.check_self_collision() or (LEVEL >= 3 and snake.check_obst_collision(obst.blocks)):
                print("Shield used!")
                active_buster = None
        else:
            if snake.check_wall_collision() or snake.check_self_collision() or snake.check_obst_collision(obst.blocks):
                game_status = "game_over"
        #останавливаю действие нитро и словера
        if active_buster in ["nitro", "slower"]:
            if pygame.time.get_ticks() - buster_timer > 5000:
                if active_buster == "nitro":
                    FPS -= 3
                elif active_buster == "slower":
                    FPS += 3
                active_buster = None

    #переход на экран гейм овер
    if game_status == "game_over":
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    game_status = "menu"
                    name_input_flag = True
                    reset_game()
                if event.key == K_SPACE:
                    game_status = "game"
                    reset_game()
        
        screen.fill(RED)
        screen.blit(game_over, (110, 170))
        score1=font_small.render(f"Your score:{int(SCORE)}", True, BLACK)
        score2=font_small.render(f"Level reached:{LEVEL}", True, BLACK)
        score3=font_small.render(f"Your best:{best_score}", True, BLACK)

        if not score_saved and SCORE > 0:
            save_score(player_name, SCORE, LEVEL)
            score_saved = True
        t1=font_small.render("PRESS SPACE TO RETRY", True, BLACK)
        t2=font_small.render("PRESS ESCAPE TO MENU", True, BLACK)
        screen.blit(t1, (120, 450))
        screen.blit(t2, (120, 500))
        screen.blit(score1, (150,250))
        screen.blit(score2, (150,300))
        screen.blit(score3, (150,350))   

    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
sys.exit()