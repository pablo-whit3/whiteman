import pygame, sys, json
from pygame.locals import *
import random, time

pygame.init()

#цвета
BLUE=(0,0,255)
WHITE=(255,255,255)
RED=(255,0,0)
BLACK=(0,0,0)
GREEN=(0,255,0)

#сет экрана, переменные и надписи в игре
WIDTH=500
HEIGHT=700
power_timer=0

font=pygame.font.SysFont("Verdana",60)
font_small=pygame.font.SysFont("Verdana", 20)
game_over = font.render("GAME OVER", True, BLACK)
background = pygame.image.load("assets\Road.png")

fps=pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Racer")

#создаю лист с картинками машин
car_images = [pygame.image.load(f"assets\Player_{i}.png") for i in range(1,5)]

#функции json настройки
def load_settings():
    try:
        with open("settings.json", "r") as f:
            return json.load(f)
    except:
        return {"sound": True, "difficulty": 1, "car_color": 1, "name": "Player"}

def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f)

def load_scores():
    try:
        with open("scores.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_score(name, SCORE):
    scores = load_scores()
    scores.append({"name": name, "score": int(SCORE)})
    scores = sorted(scores, key = lambda x : x["score"], reverse = True)[:10]
    with open("scores.json", "w") as f:
        json.dump(scores, f)

#создаю врага
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets\Enemy.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40,WIDTH-40),0)
    
    def move(self):
        self.rect.move_ip(0,ENEMY_SPEED)
    
    def spawn(self):
        self.rect.center=(random.randint(40,WIDTH-40),0)
        self.timer = pygame.time.get_ticks()

    def draw(self,surface):
        surface.blit(self.image, self.rect)

#создаю игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(f"assets\Player_{car_color}.png")
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2 - 50, HEIGHT - 80)
    
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.top > 0 :
            if pressed_keys[K_UP]:
                self.rect.move_ip(0,-SPEED)
        if self.rect.bottom < HEIGHT :    
            if pressed_keys[K_DOWN]:
                self.rect.move_ip(0,SPEED)
        if self.rect.left > 0 :
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-SPEED,0)
        if self.rect.right < WIDTH :
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(SPEED,0)
    
    def draw(self,surface):
        surface.blit(self.image, self.rect)

#создаю монеты
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets\Coin.png")
        self.rect = self.image.get_rect()
        self.spawn()

    def spawn(self):
        self.weight = random.randint(1,5)
        self.rect.center = (random.randint(20,WIDTH-20),random.randint(300,HEIGHT-20))
    
    def draw(self,surface):
        surface.blit(self.image, self.rect)

#создаю препятствия
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(["barrier", "oil"])
        self.image = pygame.image.load(f"assets\{self.type}.png")
        self.rect = self.image.get_rect()
        self.spawn()

    def spawn(self):
        self.rect.center = (random.randint(40, WIDTH-40), -50)
    
    def draw(self,surface):
        surface.blit(self.image, self.rect)

    def move(self):
        self.rect.move_ip(0, ENEMY_SPEED)
        if self.rect.top > HEIGHT:
            self.kill()

#создаю бустеры
class Buster(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(["nitro", "shield"])
        self.image = pygame.image.load(f"assets\{self.type}.png")
        self.rect = self.image.get_rect()
        self.spawn()
        self.timer = pygame.time.get_ticks()

    def spawn(self):
        self.rect.center = (random.randint(40, WIDTH-40), random.randint(50, HEIGHT-50))
    
    def draw(self,surface):
        surface.blit(self.image, self.rect)

    def time_control(self):
        if pygame.time.get_ticks() - self.timer > 5000:
            self.kill()

#загрузка настроек в код
settings = load_settings()

sound_on = settings["sound"]
DIFFICULTY = settings["difficulty"]
car_color = settings["car_color"]
player_name = settings["name"]

#создаю функцию для ресета игры и ввода переменных
def reset_game():
    global p1,e1,c1
    global enemies, coins, obstacles, busters, all_sprites
    global ENEMY_SPEED, SPEED, IN_SPEED, SCORE, DISTANCE, COINS, BOUNDARY, BONUSES, active_buster, MAX_OBSTACLES, DIFFICULTY, SLOWED, slow_timer, score_saved
    ENEMY_SPEED=5
    IN_SPEED=5
    SPEED=IN_SPEED
    SCORE=0
    DISTANCE=0
    COINS=0
    BOUNDARY=10
    BONUSES=0
    MAX_OBSTACLES=DIFFICULTY
    active_buster=None
    slow_timer=0
    score_saved = False
    SLOWED = False
    p1=Player()
    e1=Enemy()
    c1=Coin()

    enemies=pygame.sprite.Group()
    enemies.add(e1)

    coins=pygame.sprite.Group()
    coins.add(c1)

    obstacles=pygame.sprite.Group()
    obstacles.add(Obstacle())

    busters=pygame.sprite.Group()
    busters.add(Buster())

    all_sprites = pygame.sprite.Group()
    all_sprites.add(e1)
    all_sprites.add(p1)

#создаю новый ивент
new_speed = pygame.USEREVENT+1
pygame.time.set_timer(new_speed, 5000)
spawn = pygame.USEREVENT+2
pygame.time.set_timer(spawn, 1000)

#game loop and event loop
game_status = "menu"
name_input_flag = False
running=True
while running:
    #режим главного меню
    if game_status == "menu":
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    settings = load_settings()
                    car_color = settings["car_color"]
                    DIFFICULTY = settings["difficulty"]
                    game_status = "game"
                    reset_game()
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

    #режим меню настроек
    if game_status == "settings":
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    save_settings({"sound" : sound_on, "difficulty" : DIFFICULTY, "car_color": car_color, "name": player_name})
                    game_status = "menu"
                if event.key == K_1:
                    DIFFICULTY = 1
                if event.key == K_2:
                    DIFFICULTY = 2
                if event.key == K_3:
                    DIFFICULTY = 3
                
                if event.key == K_c:
                    car_color = (car_color % 4) + 1
                if event.key == K_m:
                    sound_on = not sound_on

                if event.key == K_RETURN:
                    name_input_flag = not name_input_flag
                elif name_input_flag:
                    if event.key == K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        if len(player_name) < 12:
                            player_name += event.unicode
        
        
        screen.fill(WHITE)

        t1=font_small.render("SETTINGS", True, BLACK)
        t2=font_small.render(f"Sound (M): {'ON' if sound_on else 'OFF'}", True, BLACK)
        t3=font_small.render(f"Difficulty(1-3): {DIFFICULTY}", True, BLACK)
        t4=font_small.render("Press C to change the car color", True, BLACK)
        t5=font_small.render(f"Name: {player_name}", True, BLACK)
        t6=font_small.render("ESC to save and go back", True, BLACK)
        t7=font_small.render("ENTER to change or save name", True, BLACK)

        screen.blit(t1, (180, 30))
        screen.blit(t2, (100, 200))
        screen.blit(t3, (100, 250))
        screen.blit(t4, (100, 300))
        screen.blit(t5, (100, 500))
        screen.blit(t6, (100, 100))
        screen.blit(t7, (100, 450))

        preview=car_images[car_color - 1]
        screen.blit(preview, (200, 350))

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
            t = font_small.render(f"{i+1}. {s['name']} - {s['score']}", True, BLACK)
            screen.blit(t, (100, y))
            y+=40
        
        pygame.display.flip()
        continue

    #режим гейм овер
    if game_status == "game_over":
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    game_status = "menu"
                    reset_game()
                if event.key == K_SPACE:
                    game_status = "game"
                    reset_game()
        SCORE=DISTANCE+COINS*10+BONUSES*10
        screen.fill(RED)
        screen.blit(game_over, (60, 100))
        score1 = font_small.render(f"Your score:{int(SCORE)}", True, BLACK)
        final_dist = font_small.render(f"Your distance:{int(DISTANCE)}", True, BLACK)
        final_coins = font_small.render(f"Your coins:{int(COINS)}", True, BLACK)
        screen.blit(score1, (170,450))
        screen.blit(final_dist, (170,500))
        screen.blit(final_coins, (170,550))
        if not score_saved and SCORE > 0:
            save_score(player_name, SCORE)
            score_saved = True
        t1=font_small.render("PRESS SPACE TO RETRY", True, BLACK)
        t2=font_small.render("PRESS ESCAPE TO MENU", True, BLACK)
        screen.blit(t1, (120, 300))
        screen.blit(t2, (120, 350))
        pygame.display.flip()
        continue

    DISTANCE+=SPEED * 0.1
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running=False
        if event.type == new_speed:
            ENEMY_SPEED=ENEMY_SPEED+0.5 
            print("Enemies' speed has been increased")
        if event.type == spawn:
            if random.random() < 0.3:
                busters.add(Buster())
            if len(obstacles) < MAX_OBSTACLES:
                obstacles.add(Obstacle())
            if len(enemies) < MAX_OBSTACLES:
                enemy = Enemy()
                enemies.add(enemy)
                all_sprites.add(enemy)

    #начало игры
    #прорисовка среды
    screen.blit(background, (0,0))
    dist=font_small.render(f"DISTANCE:{int(DISTANCE)}", True, BLACK)
    screen.blit(dist, (10,10))
    collected_coins=font_small.render(f"TOTAL COINS:{str(COINS)}", True, BLACK)
    screen.blit(collected_coins, (320,10))
    if active_buster:
        power_text = font_small.render(f"POWER: {active_buster}", True, RED)
        screen.blit(power_text, (10,70))

    #запускаю движение и прорисовка машин
    for entity in all_sprites:
        screen.blit(entity.image, entity.rect)
        entity.move()

    #респавн врагов
    for entity in enemies:
        if entity.rect.top > HEIGHT:
            entity.kill()

    #прорисовка монет
    for entity in coins:
        screen.blit(entity.image, entity.rect)

    #спавн препятствий
    for entity in obstacles:
        screen.blit(entity.image, entity.rect)
        entity.move()

    #спавн бустеров
    for entity in busters:
        screen.blit(entity.image, entity.rect)
        entity.time_control()

    #подбор монет
    if pygame.sprite.spritecollideany(p1,coins):
        if sound_on:
            pygame.mixer.Sound("assets\collected.mp3").play()
        COINS=COINS+c1.weight
        c1.spawn()

    #увеличиваю скорость врагов при подборе N монет и увеличиваю N
    if COINS >= BOUNDARY:
        BOUNDARY+=10
        ENEMY_SPEED=ENEMY_SPEED+1
        print("Passed the boundary")

    #столкновение с преградой
    hit = pygame.sprite.spritecollideany(p1, obstacles)
    if hit:
        if active_buster == "shield":
            active_buster = None
            hit.kill()
        else:
            IN_SPEED = max(2,IN_SPEED - 2)
            slow_timer=pygame.time.get_ticks()
            SLOWED = True
            hit.kill()
    if SLOWED:
        if pygame.time.get_ticks() - slow_timer > 3000:
            IN_SPEED = 5
            SLOWED = False

    #подбор бустеров
    hit = pygame.sprite.spritecollideany(p1, busters)
    if hit:
        BONUSES=BONUSES+1
        if active_buster == "nitro":
            IN_SPEED = 5
        active_buster = hit.type
        buster_timer = pygame.time.get_ticks()
        hit.kill()

    #эффекты бустеров
    if active_buster == "nitro":
        SPEED = IN_SPEED*2
        if pygame.time.get_ticks() - buster_timer > 5000:
            SPEED = IN_SPEED
            active_buster = None
    else:
        SPEED = IN_SPEED
    if active_buster == "shield":
        pass

    #столкновение машин и гейм овер
    if pygame.sprite.spritecollideany(p1,enemies):
        if sound_on:
            pygame.mixer.Sound("assets\crash.mp3").play()
        time.sleep(0.5)
        for entity in all_sprites:
            entity.kill()
        game_status = "game_over"

    pygame.display.flip()
    fps.tick(60)
pygame.quit()
sys.exit()