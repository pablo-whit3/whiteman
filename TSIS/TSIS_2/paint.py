import pygame, math
import datetime, collections

#сет экрана слоя и объявление некоторых переменных
def main():
    pygame.init()
    WIDTH=640
    HEIGHT=480
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Paint")
    clock = pygame.time.Clock()
    base_layer = pygame.Surface((WIDTH, HEIGHT))

    font = pygame.font.SysFont(None, 24)
    width = 5
    mode = "line"
    color=(0,0,255)
    drawing = False
    text_mode = False
    text_input = None
    text_pos=(0,0)
    points = []
    
    currX = 0
    currY = 0

    prevX = 0
    prevY = 0
    
    while True:
        
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if text_mode:
                        text_mode = False
                        text_input = ""
            
                # выбор режима рисования и цвета по нажатию клавиш
                if text_mode == True:
                    pass
                else:
                    if event.key == pygame.K_l:
                        mode = "line"
                    elif event.key == pygame.K_c:
                        mode = "circle"
                    elif event.key == pygame.K_p:
                        mode = "pencil"
                    elif event.key == pygame.K_r:
                        mode = "rect"
                    elif event.key == pygame.K_e:
                        mode = "eraser"
                    elif event.key == pygame.K_h:
                        mode = "rhombus"
                    elif event.key == pygame.K_t:
                        mode = "eq_triangle"
                    elif event.key == pygame.K_y:
                        mode = "right_triangle"
                    elif event.key == pygame.K_s:
                        mode = "square"
                    elif event.key == pygame.K_f:
                        mode = "fill"
                    elif event.key == pygame.K_x:
                        mode = "text"

                if event.key == pygame.K_1:
                    color = (255,0,0)
                elif event.key == pygame.K_2:
                    color = (0,255,0)
                elif event.key == pygame.K_3:
                    color = (0,0,255) 
                elif event.key == pygame.K_4:
                    color = (255,255,255)           

                if event.key == pygame.K_EQUALS: # "=" толщина увеличивается
                    width = min(200, width + 1)
                elif event.key == pygame.K_MINUS: # "-" толщина уменьшается
                    width = max(1, width - 1)
                
                #режимы толщины
                if event.key == pygame.K_7:
                    width = 2
                elif event.key == pygame.K_8:
                    width = 5
                elif event.key == pygame.K_9:
                    width = 10


                #сохранение
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    filename = datetime.datetime.now().strftime("drawing_%Y%m%d_%H%M%S.png")
                    pygame.image.save(base_layer, filename)
                    print("Saved:", filename)

                #текстовый режим
                if text_mode:
                    if event.key == pygame.K_RETURN:
                        img = font.render(text_input, True, color)
                        base_layer.blit(img, text_pos)
                        text_mode = False
                        text_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_input = text_input[:-1]
                    else:
                        text_input += event.unicode

            
            #запись начальной точки
            if event.type == pygame.MOUSEBUTTONDOWN:
                prevX = event.pos[0]
                prevY = event.pos[1]
                
                if mode == "fill":
                    flood_fill(base_layer,prevX, prevY, color)
                    
                
                elif mode == "text":
                    text_mode = True
                    text_pos = (prevX, prevY)
                    text_input = ""

                else:
                    drawing = True
                    points = []
                screen.blit(base_layer, (0,0))
            #запись конечной точки
            if event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                currX = event.pos[0]
                currY = event.pos[1]

                if mode == "rect":
                    draw_rect(screen, prevX, prevY, currX, currY, color, width)
                    base_layer.blit(screen, (0,0))
                elif mode == "circle":
                    draw_circle(screen, prevX, prevY, currX, currY, color, width)
                    base_layer.blit(screen, (0,0))
                elif mode == "square":
                    draw_square(screen, prevX, prevY, currX, currY, color, width)
                    base_layer.blit(screen, (0,0))
                elif mode == "rhombus":
                    draw_rhombus(screen, prevX, prevY, currX, currY, color, width)
                    base_layer.blit(screen, (0,0))
                elif mode == "eq_triangle":
                    draw_equilateral_triangle(screen, prevX, prevY, currX, currY, color, width)
                    base_layer.blit(screen, (0,0))
                elif mode == "right_triangle":
                    draw_right_triangle(screen, prevX, prevY, currX, currY, color, width)
                    base_layer.blit(screen, (0,0))
                elif mode == "line":
                    pygame.draw.line(screen, color, (prevX, prevY), (currX, currY), width)
                    base_layer.blit(screen, (0,0))

            #прорисовка промежуточных фигур и финальных
            if event.type == pygame.MOUSEMOTION and drawing:
                currX = event.pos[0]
                currY = event.pos[1]
                
                if mode == "pencil":
                    if len(points) > 0:
                        drawLineBetween(screen, points[-1], event.pos, width, color)
                        drawLineBetween(base_layer, points[-1], event.pos, width, color)
                    points.append(event.pos)
                elif mode == "eraser":
                    if len(points) > 0:
                        drawLineBetween(screen, points[-1], event.pos, width, (0,0,0))
                        drawLineBetween(base_layer, points[-1], event.pos, width, (0,0,0))
                    points.append(event.pos)
                elif mode == "rect":
                    screen.blit(base_layer, (0,0))
                    draw_rect(screen, prevX, prevY, currX, currY, color, width)
                elif mode == "circle":
                    screen.blit(base_layer, (0,0))
                    draw_circle(screen, prevX, prevY, currX, currY, color, width)
                elif mode == "square":
                    screen.blit(base_layer, (0,0))
                    draw_square(screen, prevX, prevY, currX, currY, color, width)
                elif mode == "rhombus":
                    screen.blit(base_layer, (0,0))
                    draw_rhombus(screen, prevX, prevY, currX, currY, color, width)
                elif mode == "eq_triangle":
                    screen.blit(base_layer, (0,0))
                    draw_equilateral_triangle(screen, prevX, prevY, currX, currY, color, width)
                elif mode == "right_triangle":
                    screen.blit(base_layer, (0,0))
                    draw_right_triangle(screen, prevX, prevY, currX, currY, color, width)
                elif mode == "line":
                    screen.blit(base_layer, (0,0))
                    pygame.draw.line(screen, color, (prevX, prevY), (currX, currY), width)

        if text_mode:
            img = font.render(text_input, True, color)
            screen.blit(base_layer, (0,0))
            screen.blit(img, text_pos)      
        pygame.display.flip()
        clock.tick(60)

#функция для линии и ластика: прорисовка точек
def drawLineBetween(screen, start, end, width, color):
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy))
    
    for i in range(iterations):
        if iterations == 0:
            return
        else:
            progress = i / iterations
            x = int((1-progress) * start[0] + progress * end[0])
            y = int((1-progress) * start[1] + progress * end[1])
            pygame.draw.circle(screen, color, (x, y), width)

#все функции для фигур
def draw_rect(screen, prevX, prevY, currX, currY, color, width):
    x1,y1 = prevX, prevY
    x2,y2 = currX, currY
    rect = pygame.Rect(min(x1,x2), min(y1,y2), abs(x1 - x2), abs(y1 - y2))
    pygame.draw.rect(screen, color, rect, width)

def draw_circle(screen, prevX, prevY, currX, currY, color, width):
    x1,y1 = prevX, prevY
    x2,y2 = currX, currY
    radius = int(((x2 - x1)**2 + (y2 - y1)**2) ** 0.5)
    pygame.draw.circle(screen, color, (x1,y1), radius, width)

def draw_rhombus(screen, x1, y1, x2, y2, color, width):
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2

    dx = abs(x2 - x1) // 2
    dy = abs(y2 - y1) // 2

    points = [
        (cx, cy - dy),  # верх
        (cx + dx, cy),  # право
        (cx, cy + dy),  # низ
        (cx - dx, cy)   # лево
    ]

    pygame.draw.polygon(screen, color, points, width)

def draw_equilateral_triangle(screen, x1, y1, x2, y2, color, width):
    dx = x2 - x1
    dy = y2 - y1
    side = max(abs(dx), abs(dy))
    if side == 0:
        return
    height = int(side * math.sqrt(3) / 2)

    if dx >= 0:
        sx=1 
    else:
        sx=-1
    if dy >= 0:
        sy=1 
    else:
        sy=-1
    
    top_x = x1 + sx*side // 2
    top_y = y1 + sy*height

    points = [
        (x1, y1),
        (x1 + sx*side, y1),
        (top_x, top_y)
    ]

    pygame.draw.polygon(screen, color, points, width)

def draw_right_triangle(screen, x1, y1, x2, y2, color, width):
    points = [
        (x1, y1),
        (x2, y1),
        (x1, y2)
    ]

    pygame.draw.polygon(screen, color, points, width)

def draw_square(screen, x1, y1, x2, y2, color, width):
    side = min(abs(x2 - x1), abs(y2 - y1))

    x = x1 if x2 >= x1 else x1 - side
    y = y1 if y2 >= y1 else y1 - side

    rect = pygame.Rect(x, y, side, side)
    pygame.draw.rect(screen, color, rect, width)

def flood_fill(surface, x, y, new_color):
    target_color = surface.get_at((x,y))
    if target_color == new_color:
        return
    
    w,h = surface.get_size()
    queue = collections.deque([(x,y)])
    
    while queue:
        x,y = queue.popleft()
        if x < 0 or x >= w or y < 0 or y > h:
            continue
        if surface.get_at((x,y)) != target_color:
            continue

        surface.set_at((x,y), new_color)
        if x + 1 < w:
            queue.append((x+1,y))
        if x - 1 >= 0:
            queue.append((x-1,y))
        if y + 1 < h:
            queue.append((x,y+1))
        if y - 1 >= 0:
            queue.append((x,y-1))
main()