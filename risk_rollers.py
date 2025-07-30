import pygame
import random
import sys
import os

pygame.init()

# 프로그램 아이콘 설정
icon = pygame.image.load(os.path.join("src", "risk-rollers.png"))
pygame.display.set_icon(icon)

# 화면 설정 (크기 조절)
WIDTH, HEIGHT = 800, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Risk Rollers")
font = pygame.font.SysFont("malgungothic", 20)
large_font = pygame.font.SysFont("malgungothic", 28, bold=True)
clock = pygame.time.Clock()

# 색상
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY  = (200,200,200)
RED   = (255,80,80)
BLUE  = (80,80,255)
GREEN = (0,200,0)

# 버튼
ROLL_BUTTON = pygame.Rect(100, 600, 100, 40)
HOLD_BUTTON = pygame.Rect(300, 600, 100, 40)
QUIT_BUTTON = pygame.Rect(500, 600, 100, 40)

# ─── 주사위 및 효과 설정 (생략: 기존 코드와 동일) ─────────────────────────────
dice_config = {
    "Balanced":   {"faces":[1,2,3,4,5,6],    "max_rolls":6, "description":"기본형. 균형 분포."},
    "Aggressive": {"faces":[1,1,5,6,6,6],    "max_rolls":7, "description":"고점수 확률 ↑."},
    "Safe":       {"faces":[2,2,3,3,3,3],    "max_rolls":5, "description":"2 연속 2회 실패."},
    "Coin":      {"faces":[1,1,1,6,6,6],    "max_rolls":6, "description":"연속 성공 시 x2"},
    "Slot":       {"faces":[1,2,2,2,3,3],    "max_rolls":7, "description":"연속 3번 점수+"},
    "Random":       {"faces":[1,2,3,4,5,6],    "max_rolls":6, "description":"매 턴 랜덤"},
}
EFFECTS = [["plus","+2"], ["steal","1점 강탈"], ["minus","상대 -2점"], ["bonus","턴 점수 +3"],["addroll","롤 횟수 +1"]]
effect_icons = {
    "plus":      pygame.transform.scale(pygame.image.load(os.path.join("src","effect","plus.png")),      (36,36)),
    "steal":     pygame.transform.scale(pygame.image.load(os.path.join("src","effect","steal.png")),     (36,36)),
    "minus":     pygame.transform.scale(pygame.image.load(os.path.join("src","effect","minus.png")),     (36,36)),
    "bonus":     pygame.transform.scale(pygame.image.load(os.path.join("src","effect","bonus.png")),     (36,36)),
    "addroll":   pygame.transform.scale(pygame.image.load(os.path.join("src","effect","addroll.png")),   (36,36)),
}
dice_types = []
for name, cfg in list(dice_config.items()):
    entry = {"name":name,"max_rolls":cfg["max_rolls"],"description":cfg["description"],"faces_info":[]}
    key = name.lower()
    for face_value in cfg["faces"]:
        img_path = os.path.join("src", key, f"dice{face_value}.png")
        img = pygame.transform.scale(pygame.image.load(img_path), (36,36))
        entry["faces_info"].append({"value":face_value, "image":img, "effect":None})
    dice_types.append(entry)
# ────────────────────────────────────────────────────────────────────

player_states = [
    {"dice":None,"score":0,"roll_count":0,"last_roll":None,"last_last_roll":None,"threshold":0,"random":False},
    {"dice":None,"score":0,"roll_count":0,"last_roll":None,"last_last_roll":None,"threshold":0,"random":False}
]
turn_score = 0
current_player = 0
rolled_face_info = None
game_over = False

def draw_text(txt, x, y, col=BLACK, f=font):
    screen.blit(f.render(txt, True, col), (x,y))

def choose_effect(player_idx):
    # 기존 choose_effect 구현
    options = random.sample(EFFECTS, 2)
    BOX_W, BOX_H, SP = 300, 80, 20
    y = 250
    while True:
        screen.fill(WHITE)
        pygame.draw.rect(screen, RED if player_idx==0 else BLUE, (0,0,WIDTH,80))
        draw_text(f"Player {player_idx+1}: 효과 선택", WIDTH//2-100,30,WHITE, large_font)
        for i, opt in enumerate(options):
            x = WIDTH//2 - BOX_W - SP//2 + i*(BOX_W+SP)
            rect = pygame.Rect(x,y,BOX_W,BOX_H)
            pygame.draw.rect(screen,GRAY,rect, border_radius=6)
            draw_text(opt[1], x+10, y+30)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN and e.key in (pygame.K_1,pygame.K_2):
                return options[0] if e.key==pygame.K_1 else options[1]
            if e.type==pygame.MOUSEBUTTONDOWN:
                for i in range(2):
                    x = WIDTH//2 - BOX_W - SP//2 + i*(BOX_W+SP)
                    if pygame.Rect(x,y,BOX_W,BOX_H).collidepoint(e.pos):
                        return options[i]
        clock.tick(30)

def choose_face_effect(player_idx, effect):
    # 기존 choose_face_effect 구현
    ps = player_states[player_idx]
    faces_info = ps["dice"]["faces_info"]
    BOX_W, BOX_H, SP = 80,80,20
    total_w = len(faces_info)*BOX_W + (len(faces_info)-1)*SP
    start_x = (WIDTH - total_w)//2
    y = 200
    while True:
        screen.fill(WHITE)
        pygame.draw.rect(screen, RED if player_idx==0 else BLUE, (0,0,WIDTH,80))
        draw_text("효과 적용할 면 선택", WIDTH//2-100,30,WHITE, large_font)
        for i, face_info in enumerate(faces_info):
            x = start_x + i*(BOX_W+SP)
            rect = pygame.Rect(x,y,BOX_W,BOX_H)
            pygame.draw.rect(screen,GRAY,rect, border_radius=6)
            screen.blit(face_info["image"], (x+10,y+10))
            if face_info["effect"]:
                screen.blit(effect_icons[face_info["effect"]], (x+10,y+10))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                for i, face_info in enumerate(faces_info):
                    x = start_x + i*(BOX_W+SP)
                    if pygame.Rect(x,y,BOX_W,BOX_H).collidepoint(e.pos):
                        face_info["effect"] = effect
                        return
        clock.tick(30)

def select_dice(player_idx):
    BOX_W, BOX_H, SP = 150,240,20
    n = len(dice_types)
    num_per_row = (n + 1)//2
    total_w = num_per_row*BOX_W + (num_per_row-1)*SP
    start_x = (WIDTH - total_w)//2
    first_y = 150
    second_y = first_y + BOX_H + SP
    color = RED if player_idx==0 else BLUE
    while True:
        screen.fill(WHITE)
        pygame.draw.rect(screen, color, (0,0,WIDTH,80))
        draw_text(f"Player {player_idx+1} 주사위 선택", WIDTH//2-100,30,WHITE,large_font)
        for i, d in enumerate(dice_types):
            row = i // num_per_row
            col = i % num_per_row
            bx = start_x + col*(BOX_W+SP)
            by = first_y if row==0 else second_y
            pygame.draw.rect(screen,GRAY,(bx,by,BOX_W,BOX_H),border_radius=6)
            draw_text(d["name"], bx+8, by+8)
            draw_text(d["description"], bx+8, by+32)
            for j, face_info in enumerate(d["faces_info"]):
                ix = bx+8 + (j%3)*48
                iy = by+70 + (j//3)*50
                screen.blit(face_info["image"], (ix, iy))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                for i in range(n):
                    row = i // num_per_row
                    col = i % num_per_row
                    bx = start_x + col*(BOX_W+SP)
                    by = first_y if row==0 else second_y
                    if pygame.Rect(bx,by,BOX_W,BOX_H).collidepoint(e.pos):
                        selected_dice=dice_types[i].copy()
                        return selected_dice
        clock.tick(30)

def switch_player():
    global current_player, turn_score, rolled_face_info
    current_player ^= 1
    turn_score = 0
    ps = player_states[current_player]
    if ps["random"]:
        ps = randomize_dice(ps)
    ps["roll_count"] = 0
    ps["last_roll"] = None
    ps["last_last_roll"] = None

def roll_dice():
    global rolled_face_info, turn_score, game_over
    ps = player_states[current_player]
    if ps["roll_count"] >= ps["dice"]["max_rolls"]:
        return
    ps["roll_count"] += 1
    info = random.choice(ps["dice"]["faces_info"])
    rolled_face_info = info
    face = info["value"]

    # effect 적용
    eff = info["effect"]
    if eff == "plus":
        ps["score"] += 2
    elif eff == "steal":
        op = player_states[1-current_player]
        steal = min(1, op["score"])
        op["score"] -= steal
        ps["score"] += steal
    elif eff == "minus":
        op = player_states[1-current_player]
        op["score"] = max(0, op["score"]-2)
    elif eff == "bonus":
        turn_score += 3
    elif eff == "addroll":
        ps["roll_count"] -= 1

    if ps["dice"]["name"]=="Safe":
        if face==1 or (face==2 and ps["last_roll"]==2):
            turn_score=0; switch_player(); return
        ps["last_roll"]=face
    elif ps["dice"]["name"]=="Coin":
        if face==1:
            turn_score=0; switch_player(); return
        if turn_score > 0:
            turn_score *=2; return
    elif ps["dice"]["name"]=="Slot":
        if face==1:
            turn_score=0; switch_player(); return
        else:
            if ps["last_last_roll"]==ps["last_roll"]==face:
                if face==2:
                    turn_score += 5
                elif face==3:
                    turn_score += 10
            ps["last_last_roll"]=ps["last_roll"]
            ps["last_roll"]=face

    elif face==1:
        turn_score=0; switch_player(); return
    turn_score += face

def hold():
    global turn_score, game_over
    ps = player_states[current_player]
    ps["score"] += turn_score
    new_thresh = ps["score"]//20
    if new_thresh > ps["threshold"] and ps["score"]<100:
        ps["threshold"] = new_thresh
        opponent = 1 - current_player
        eff = choose_effect(opponent)
        choose_face_effect(opponent, eff[0])
    if ps["score"]>=100:
        game_over = True
    else:
        switch_player()

def draw_ui():
    screen.fill(WHITE)
    pygame.draw.rect(screen, RED if current_player==0 else BLUE, (0,0,WIDTH,80))
    for idx in (0,1):
        ps = player_states[idx]
        x = 20 if idx==0 else WIDTH-240
        col = WHITE if current_player==idx else BLACK
        draw_text(f"P{idx+1}: {ps['score']}  Dice: {ps['dice']['name']}", x, 20, col)
        draw_text(f"Rolls: {ps['roll_count']}/{ps['dice']['max_rolls']}", x, 40, col)
    draw_text(f"▶ Player {current_player+1} Turn", WIDTH//2-100,100,WHITE,large_font)
    draw_text(f"Turn Score: {turn_score}", WIDTH//2-60,140)
    clr = RED if current_player==0 else BLUE
    pygame.draw.rect(screen, clr, ROLL_BUTTON); draw_text("Roll", ROLL_BUTTON.x+25,ROLL_BUTTON.y+10,WHITE)
    pygame.draw.rect(screen, clr, HOLD_BUTTON); draw_text("Hold", HOLD_BUTTON.x+25,HOLD_BUTTON.y+10,WHITE)
    pygame.draw.rect(screen, GRAY, QUIT_BUTTON); draw_text("Quit", QUIT_BUTTON.x+25,QUIT_BUTTON.y+10,BLACK)
    if rolled_face_info:
        img = pygame.transform.scale(rolled_face_info["image"], (100,100))
        screen.blit(img,(WIDTH//2-50,200))
        if rolled_face_info["effect"]:
            screen.blit(pygame.transform.scale(effect_icons[rolled_face_info["effect"]],(100,100)),(WIDTH//2-50,200))
    if game_over:
        draw_text(f"🎉 Player {current_player+1} Wins!",WIDTH//2-140,320,GREEN,large_font)
    pygame.display.flip()

def randomize_dice(ps):
    ps["random"] = True
    selection=random.choice(dice_types[:-1]).copy()
    ps["dice"]["name"] = selection["name"]
    ps["dice"]["max_rolls"] = selection["max_rolls"]
    for i in range(len(selection["faces_info"])):
        ps["dice"]["faces_info"][i]["value"]=selection["faces_info"][i]["value"]
        ps["dice"]["faces_info"][i]["image"]=selection["faces_info"][i]["image"]
    return ps

# 초기 주사위 선택
player_states[0]["dice"] = select_dice(0)
player_states[1]["dice"] = select_dice(1)

if player_states[1]["dice"]["name"] == "Random":
    player_states[1] = randomize_dice(player_states[1])
if player_states[0]["dice"]["name"] == "Random":
    player_states[0] = randomize_dice(player_states[0])

# 메인 루프
while True:
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            pygame.quit(); sys.exit()
        if not game_over:
            if e.type==pygame.KEYDOWN:
                if current_player==0 and e.key in (pygame.K_a,pygame.K_s):
                    roll_dice() if e.key==pygame.K_a else hold()
                if current_player==1 and e.key in (pygame.K_l,pygame.K_k):
                    roll_dice() if e.key==pygame.K_l else hold()
            if e.type==pygame.MOUSEBUTTONDOWN:
                if ROLL_BUTTON.collidepoint(e.pos):
                    roll_dice()
                elif HOLD_BUTTON.collidepoint(e.pos):
                    hold()
                elif QUIT_BUTTON.collidepoint(e.pos):
                    pygame.quit(); sys.exit()
    draw_ui()
    clock.tick(30)

