import pygame, sys, json
from pygame.locals import *
import random, time

pygame.init()


fps=pygame.time.Clock()

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
player_name = "Player"

font=pygame.font.SysFont("Verdana",60)
font_small=pygame.font.SysFont("Verdana", 20)
game_over = font.render("GAME OVER", True, BLACK)
background = pygame.image.load("assets\Road.png")

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Racer")

#функции json настройки
def load_settings():
    try:
        with open("settings.json", "r") as f:
            return json.load(f)
    except:
        return {"sound": True, "difficulty": 1}

def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f)

def load_scores():
    try:
        with open("scores.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_score(name, SCORE, COINS, BONUSES):
    scores = load_scores()
    scores.append({"name": name, "score": int(SCORE), "coins": COINS, "bonuses": BONUSES})
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
        global SCORE
        self.rect.move_ip(0,ENEMY_SPEED)
        if self.rect.top > HEIGHT :
            self.rect.top=0
            self.rect.center=(random.randint(40,WIDTH-40),0)
    
    def draw(self,surface):
        surface.blit(self.image, self.rect)

#создаю игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets\Player.png")
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

#создаю функцию для ресета игры и ввода переменных
def reset_game():
    global p1,e1,c1
    global enemies, coins, obstacles, busters, all_sprites
    global ENEMY_SPEED, SPEED, IN_SPEED, SCORE, DISTANCE, COINS, BOUNDARY, BONUSES, active_buster, MAX_OBSTACLES, DIFFICULTY, SLOWED, slow_timer
    ENEMY_SPEED=5
    IN_SPEED=5
    SPEED=IN_SPEED
    SCORE=0
    DISTANCE=0
    COINS=0
    BOUNDARY=10
    BONUSES=0
    DIFFICULTY=3
    MAX_OBSTACLES=DIFFICULTY
    active_buster=None
    slow_timer=0
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
running=True
while running:
    #переходы между меню
    if game_status == "menu":
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    game_status = "game"
                    reset_game()
        
        screen.fill(WHITE)
        t1=font.render("PRESS SPACE", True, BLACK)
        t2=font.render("TO START", True, BLACK)
        screen.blit(t1, (50, 300))
        screen.blit(t2, (100, 370))
        pygame.display.flip()
        continue

    if game_status == "game_over":
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    game_status = "menu"
                    reset_game()
        SCORE=DISTANCE+COINS*10+BONUSES*10
        screen.fill(RED)
        screen.blit(game_over, (60, 100))
        score1 = font_small.render(f"Your score:{int(SCORE)}", True, BLACK)
        screen.blit(score1, (170,450))
        screen.blit(final_dist, (170,500))
        save_score(player_name, SCORE, COINS, BONUSES)
        t=font_small.render("PRESS SPACE TO MENU", True, BLACK)
        screen.blit(t, (120, 300))
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
            busters.add(Buster())
            if len(obstacles) < MAX_OBSTACLES:
                obstacles.add(Obstacle())


    #прорисовка среды
    screen.blit(background, (0,0))
    dist=font_small.render(f"DISTANCE:{int(DISTANCE)}", True, BLACK)
    screen.blit(dist, (10,10))
    collected_coins=font_small.render(f"TOTAL COINS:{str(COINS)}", True, BLACK)
    screen.blit(collected_coins, (320,10))
    final_dist = font_small.render(f"Your distance:{int(DISTANCE)}", True, BLACK)
    if active_buster:
        power_text = font_small.render(f"POWER: {active_buster}", True, RED)
        screen.blit(power_text, (10,70))

    #запускаю движение и прорисовка машин
    for entity in all_sprites:
        screen.blit(entity.image, entity.rect)
        entity.move()

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

    #столкновение машин
    if pygame.sprite.spritecollideany(p1,enemies):
        pygame.mixer.Sound("assets\crash.mp3").play()
        time.sleep(0.5)
        for entity in all_sprites:
            entity.kill()
        game_status = "game_over"

    pygame.display.flip()
    fps.tick(60)
pygame.quit()
sys.exit()