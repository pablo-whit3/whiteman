import pygame
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Player")

font = pygame.font.SysFont(None, 30)

music = "music"
playlist = [f for f in os.listdir(music) if f.endswith((".mp3", ".wav"))]

track_lengths = {
    "Noize MC - Вселенная бесконечна (cdn.zvuki.me).mp3": 260,
    "Noize MC - Выдыхай (cdn.zvuki.me).mp3": 192,
    "Noize MC - Любимый цвет (cdn.zvuki.me).mp3": 151,

}

current_track = 0
playing = False
paused = False
total_length = 0


def load_track(index):
    global total_length

    track_name = playlist[index]
    track_path = os.path.join(music, track_name)

    pygame.mixer.music.load(track_path)

    total_length = track_lengths.get(track_name, 0)


def get_current_time():
    pos_ms = pygame.mixer.music.get_pos()
    pos_sec = max(0, pos_ms // 1000)

    minutes = pos_sec // 60
    seconds = pos_sec % 60

    return f"{minutes:02}:{seconds:02}"


def get_total_time():
    if total_length == 0:
        return "??:??"

    minutes = total_length // 60
    seconds = total_length % 60

    return f"{minutes:02}:{seconds:02}"


def draw():
    screen.fill((30, 30, 30))

    if playlist:
        track_text = font.render(f"Track: {playlist[current_track]}", True, (255, 255, 255))
        screen.blit(track_text, (20, 40))
  

        time_text = font.render(
            f"{get_current_time()} / {get_total_time()}",
            True,
            (255, 255, 255)
        )
        screen.blit(time_text, (20, 120))

    else:
        text = font.render("No music files found!", True, (255, 0, 0))
        screen.blit(text, (20, 50))

    controls = [
        "P = Play / Resume",
        "S = Pause",
        "N = Next",
        "B = Back",
        "Q = Quit"
    ]

    for i, c in enumerate(controls):
        t = font.render(c, True, (180, 180, 180))
        screen.blit(t, (20, 170 + i * 25))

    pygame.display.flip()


if playlist:
    load_track(current_track)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_p:
                if not playing:
                    pygame.mixer.music.play()
                    playing = True
                    paused = False
                elif paused:
                    pygame.mixer.music.unpause()
                    paused = False

            elif event.key == pygame.K_s:
                if playing and not paused:
                    pygame.mixer.music.pause()
                    paused = True

            elif event.key == pygame.K_n:
                current_track = (current_track + 1) % len(playlist)
                load_track(current_track)
                pygame.mixer.music.play()
                playing = True
                paused = False

            elif event.key == pygame.K_b:
                current_track = (current_track - 1) % len(playlist)
                load_track(current_track)
                pygame.mixer.music.play()
                playing = True
                paused = False

            elif event.key == pygame.K_q:
                running = False   

    draw()
    clock.tick(60)

pygame.quit()