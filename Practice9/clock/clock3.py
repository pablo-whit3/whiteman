import pygame
import time
import math

pygame.init()

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey Clock")

CENTER = (WIDTH // 2, HEIGHT // 2)
RADIUS = 300

minute_img = pygame.image.load("images/min hand clock.png").convert_alpha()
second_img = pygame.image.load("images/sec hand clock.png").convert_alpha()

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 40)


def get_time():
    t = time.localtime()
    return t.tm_hour, t.tm_min, t.tm_sec


def blit_rotated(image, angle):
    rotated = pygame.transform.rotate(image, -angle)
    rect = rotated.get_rect(center=CENTER)
    screen.blit(rotated, rect)


def draw_marks():
    for sec in [0, 15, 30, 45]:
        angle = math.radians(sec * 6 - 90)

        x1 = CENTER[0] + (RADIUS - 20) * math.cos(angle)
        y1 = CENTER[1] + (RADIUS - 20) * math.sin(angle)

        x2 = CENTER[0] + RADIUS * math.cos(angle)
        y2 = CENTER[1] + RADIUS * math.sin(angle)

        pygame.draw.line(screen, (0, 0, 0), (x1, y1), (x2, y2), 4)


def draw_digital_time(h, m, s):
    time_str = f"{h:02}:{m:02}:{s:02}"
    text = font.render(time_str, True, (0, 0, 0))
    rect = text.get_rect(center=(CENTER[0], CENTER[1] + 350))
    screen.blit(text, rect)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    hours, minutes, seconds = get_time()

    second_angle = seconds * 6
    minute_angle = minutes * 6 + seconds * 0.1

    screen.fill((0, 0, 255))

    draw_marks()

    pygame.draw.circle(screen, (0, 0, 0), CENTER, 6)

    blit_rotated(second_img, second_angle)
    blit_rotated(minute_img, minute_angle)

    draw_digital_time(hours, minutes, seconds)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()