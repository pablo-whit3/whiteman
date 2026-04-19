import pygame

pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball")

WHITE = (255, 255, 255)
RED = (255, 0, 0)

radius = 25
x, y = WIDTH // 2, HEIGHT // 2
speed = 20

clock = pygame.time.Clock()
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if x - speed - radius >= 0:
                    x -= speed

            elif event.key == pygame.K_RIGHT:
                if x + speed + radius <= WIDTH:
                    x += speed

            elif event.key == pygame.K_UP:
                if y - speed - radius >= 0:
                    y -= speed

            elif event.key == pygame.K_DOWN:
                if y + speed + radius <= HEIGHT:
                    y += speed

    pygame.draw.circle(screen, RED, (x, y), radius)

    klava = pygame.key.get_pressed()

    if klava[pygame.K_s]:
        if y + speed + radius <= HEIGHT:
            y += speed



    pygame.display.flip()
    clock.tick(60)

pygame.quit()