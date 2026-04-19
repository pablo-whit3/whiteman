import pygame
import time

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey Clock")

CENTER = (WIDTH // 2, HEIGHT // 2)

# --- загрузка изображений ---
second_img = pygame.image.load("images/sec hand clock.png").convert_alpha()
minute_img = pygame.image.load("images/min hand clock.png").convert_alpha()


clock = pygame.time.Clock()


def get_time():
    t = time.localtime()
    return t.tm_min, t.tm_sec


def blit_rotate_pivot(image, angle, pivot, length):
    """
    pivot = точка центра часов
    length = насколько далеко основание стрелки от центра внутри картинки
    """

    rotated_image = pygame.transform.rotate(image, -angle)

    # направление "вверх" после поворота
    rad = angle * 3.14159265 / 180

    # смещение так, чтобы основание стрелки было в центре
    offset_x = -length * pygame.math.Vector2(1, 0).rotate(angle).x
    offset_y = -length * pygame.math.Vector2(1, 0).rotate(angle).y

    rect = rotated_image.get_rect(center=(pivot[0] + offset_x, pivot[1] + offset_y))

    screen.blit(rotated_image, rect)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    minutes, seconds = get_time()

    # --- углы ---
    second_angle = seconds * 6
    minute_angle = minutes * 6 + seconds * 0.1

    # --- фон ---
    screen.fill((255, 255, 255))

    # центр часов
    pygame.draw.circle(screen, (0, 0, 0), CENTER, 6)

    # --- длины стрелок (настраиваются под твои PNG) ---
    SECOND_LENGTH = 80
    MINUTE_LENGTH = 60

    # --- стрелки ---
    blit_rotate_pivot(second_img, second_angle, CENTER, SECOND_LENGTH)
    blit_rotate_pivot(minute_img, minute_angle, CENTER, MINUTE_LENGTH)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()