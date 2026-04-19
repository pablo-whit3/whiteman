import pygame
import time

pygame.init()

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey Clock")

CENTER = (WIDTH // 2, HEIGHT // 2)

minute_img = pygame.image.load("images/min hand clock.png").convert_alpha()
second_img = pygame.image.load("images/sec hand clock.png").convert_alpha()


clock = pygame.time.Clock()


def get_time():
    t = time.localtime()
    return t.tm_min, t.tm_sec


def blit_rotated(image, angle):
    """вращает картинку и центрирует в одну точку"""
    rotated = pygame.transform.rotate(image, -angle)
    rect = rotated.get_rect(center=CENTER)
    screen.blit(rotated, rect)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- время ---
    minutes, seconds = get_time()

    # --- углы ---
    second_angle = seconds * 6                  # 360/60
    minute_angle = minutes * 6 + seconds * 0.1  # плавность

    # --- фон ---
    screen.fill((0, 0, 255))

    # центр (точка крепления стрелок)
    pygame.draw.circle(screen, (0, 0, 0), CENTER, 6)

    # --- стрелки ---
    blit_rotated(second_img, second_angle)  # секундная
    blit_rotated(minute_img, minute_angle)  # минутная

    pygame.display.flip()
    clock.tick(60)

pygame.quit()