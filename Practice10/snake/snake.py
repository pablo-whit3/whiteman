import pygame, sys
import random

pygame.init()

#ввожу постоянные и переменные
WIDTH = 600
HEIGHT = 600
WHITE = (255,255,255)
BLACK = (0,0,0)
GREY = (200,200,200)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
CELL = 30
FPS = 5
SCORE = 0
LEVEL = 1
FOOD_TO_PASS=5

#сет экрана
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, 650))
pygame.display.set_caption("Snake")

#рендер надписей
font=pygame.font.SysFont("Verdana",60)
font_small=pygame.font.SysFont("Verdana", 20)
game_over = font.render("GAME OVER", True, BLACK)

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
            pygame.draw.rect(screen, YELLOW, (segment.x*CELL, segment.y*CELL, CELL, CELL))

    #подбор еды    
    def check_collision(self,food):
        global SCORE, FPS, LEVEL, FOOD_TO_PASS
        head=self.body[0]
        if head.x == food.pos.x and head.y == food.pos.y:
            print("Got food!")
            SCORE+=1
            self.body.append(Point(head.x, head.y))
            food.spawn(snake.body)
        if SCORE >= FOOD_TO_PASS:
            LEVEL+=1
            FPS+=1
            FOOD_TO_PASS+=5  

    #запрет на столкновение с собой
    def check_self_collision(self):
        head = self.body[0]
        for segment in self.body[1:]:
            if head.x == segment.x and head.y == segment.y:
                return True
        return False  

#создаю класс для еды
class Food:
    def __init__(self):
        self.pos = Point(9,9)

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.pos.x*CELL, self.pos.y*CELL, CELL, CELL))

    def spawn(self, snake_body):
        while True:
            self.pos.x = random.randint(0, WIDTH // CELL - 1)
            self.pos.y = random.randint(0, HEIGHT // CELL - 1)

            ok = True
            for s in snake_body:
                if s.x == self.pos.x and s.y == self.pos.y:
                    ok = False
                    break

            if ok:
                break

food = Food()
snake = Snake()

running = True
game_over_flag = False
while running:
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
    draw_grid()
    score=font_small.render(f"SCORE:{int(SCORE)}", True, WHITE)
    screen.blit(score, (10,610))
    current_level=font_small.render(f"LEVEL:{str(LEVEL)}", True, WHITE)
    screen.blit(current_level, (320,610))

    if not game_over_flag:
        snake.move()
        if snake.check_wall_collision() or snake.check_self_collision():
            game_over_flag = True
        snake.check_collision(food)

    snake.draw()
    food.draw()

    if game_over_flag:
        screen.fill(RED)
        screen.blit(game_over, (110, 200))
        score1=font_small.render(f"Your score:{int(SCORE)}", True, BLACK)
        screen.blit(score1, (150,300))    

    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
sys.exit()