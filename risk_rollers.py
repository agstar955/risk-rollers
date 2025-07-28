import pygame
import random
import sys

pygame.init()

# 화면 설정
WIDTH, HEIGHT = 700, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Risk Rollers")
clock = pygame.time.Clock()

font = pygame.font.SysFont("malgungothic", 20)
large_font = pygame.font.SysFont("malgungothic", 28, bold=True)

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 80, 80)
BLUE = (80, 80, 255)

# 버튼
ROLL_BUTTON = pygame.Rect(100, 400, 100, 40)
HOLD_BUTTON = pygame.Rect(250, 400, 100, 40)
QUIT_BUTTON = pygame.Rect(400, 400, 100, 40)

# 주사위 정의 (하위 폴더 구조: dice_images/<type>/dice<i>.png)
dice_types = [
    {"name": "Balanced",   "faces": [1, 2, 3, 4, 5, 6],      "description": "기본형. 균형 잡힌 분포."},
    {"name": "Aggressive", "faces": [4, 5, 6, 6, 6, 1],      "description": "공격적. 고점수 확률 높음."},
    {"name": "Safe",       "faces": [2, 3, 3, 4, 4, 5],      "description": "1 없음. 안정적 수익."},
    {"name": "Risky",      "faces": [1, 1, 1, 6, 6, 6],      "description": "하이 리스크 하이 리턴."}
]

# 각 주사위 타입별 얼굴 이미지 로딩
for dice in dice_types:
    key = dice["name"].lower()  # "balanced", "aggressive", etc.
    dice["images"] = []
    for i in range(1, 7):
        path = f'dice_images/{key}/dice{i}.png'
        img = pygame.image.load(path)
        img = pygame.transform.scale(img, (40, 40))
        dice["images"].append(img)

# 상태 변수
player_dice = [None, None]
players = [0, 0]
turn_score = 0
current_player = 0
die_value = 0
game_over = False

def draw_text(text, x, y, color=BLACK, font_obj=font):
    img = font_obj.render(text, True, color)
    screen.blit(img, (x, y))

def select_dice(player_index):
    selecting = True
    selected = None
    while selecting:
        screen.fill(WHITE)
        draw_text(f"Player {player_index+1} 주사위 선택", 220, 30, font_obj=large_font)
        for i, dice in enumerate(dice_types):
            bx = 60 + i * 150
            by = 100
            pygame.draw.rect(screen, GRAY, (bx, by, 130, 180))
            # 이름, 설명
            draw_text(dice["name"], bx + 10, by + 10)
            draw_text(dice["description"], bx + 10, by + 40)
            # 눈 배열에 따른 얼굴 이미지 표시 (2행×3열)
            for j, face in enumerate(dice["faces"]):
                ix = bx + 10 + (j % 3) * 45
                iy = by + 80 + (j // 3) * 45
                img = dice["images"][face - 1]
                screen.blit(img, (ix, iy))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(len(dice_types)):
                    if pygame.Rect(60 + i * 150, 100, 130, 180).collidepoint(event.pos):
                        selected = dice_types[i]
                        selecting = False
        clock.tick(30)
    return selected

def draw_ui():
    screen.fill(WHITE)
    # 상단 정보
    pygame.draw.rect(screen, RED if current_player==0 else BLUE, (0, 0, WIDTH, 80))
    draw_text(f"P1: {players[0]}", 20, 20, WHITE)
    draw_text(f"P2: {players[1]}", WIDTH - 100, 20, WHITE)
    draw_text(f"▶ Player {current_player+1}'s Turn", 250, 100, WHITE, font_obj=large_font)
    # 버튼
    pygame.draw.rect(screen, RED if current_player==0 else BLUE, ROLL_BUTTON)
    draw_text("Roll", ROLL_BUTTON.x + 25, ROLL_BUTTON.y + 10, WHITE)
    pygame.draw.rect(screen, RED if current_player==0 else BLUE, HOLD_BUTTON)
    draw_text("Hold", HOLD_BUTTON.x + 25, HOLD_BUTTON.y + 10, WHITE)
    pygame.draw.rect(screen, GRAY, QUIT_BUTTON)
    draw_text("Quit", QUIT_BUTTON.x + 25, QUIT_BUTTON.y + 10, BLACK)
    # 주사위 눈 이미지
    if die_value > 0:
        img = player_dice[current_player]["images"][die_value - 1]
        screen.blit(pygame.transform.scale(img, (100, 100)), (WIDTH//2 - 50, 200))
    pygame.display.flip()

def roll_dice():
    global die_value, turn_score, current_player
    faces = player_dice[current_player]["faces"]
    die_value = random.choice(faces)
    if die_value == 1:
        turn_score = 0
        current_player = 1 - current_player
    else:
        turn_score += die_value

def hold():
    global players, turn_score, current_player, game_over
    players[current_player] += turn_score
    turn_score = 0
    if players[current_player] >= 100:
        game_over = True
    else:
        current_player = 1 - current_player

# 주사위 선택
player_dice[0] = select_dice(0)
player_dice[1] = select_dice(1)

# 메인 루프
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
            if ROLL_BUTTON.collidepoint(event.pos):
                roll_dice()
            elif HOLD_BUTTON.collidepoint(event.pos):
                hold()
            elif QUIT_BUTTON.collidepoint(event.pos):
                pygame.quit()
                sys.exit()
        if not game_over and event.type == pygame.KEYDOWN:
            if current_player == 0 and event.key in (pygame.K_a, pygame.K_s):
                roll_dice() if event.key == pygame.K_a else hold()
            if current_player == 1 and event.key in (pygame.K_l, pygame.K_k):
                roll_dice() if event.key == pygame.K_l else hold()
    draw_ui()
    clock.tick(30)
