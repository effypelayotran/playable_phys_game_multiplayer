import os
import socket
import pickle
import pygame
import gameParameters
from stage import Stage
from ship import Ship
from blackhole import Blackhole

# Path to custom font
FONT_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'Hyperspace.otf')

# Server settings
SERVER_ADDR = ("45.79.130.19", 5600)
BUFFER_SIZE = 65536

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 232, 31)
DARK = (10, 10, 10)

def draw_button(surface, rect, text, font, fill_color=BLACK, text_color=WHITE, outline_color=YELLOW):
    pygame.draw.rect(surface, fill_color, rect)
    pygame.draw.rect(surface, outline_color, rect, 3)
    txt = font.render(text, True, text_color)
    txt_rect = txt.get_rect(center=rect.center)
    surface.blit(txt, txt_rect)

class Network:
    def __init__(self, num_players=5):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.s.connect(SERVER_ADDR)
        print(str(num_players))
        self.s.sendall(str(num_players).encode())
        init = self.s.recv(2048).decode()
        if init.startswith("too many"):
            raise RuntimeError(init)
        self.player = int(init)
    def send(self, action):
        self.s.sendall(str(action).encode())
        data = self.s.recv(BUFFER_SIZE)
        return pickle.loads(data)


def menu_screen(screen, clock):
    """Display start menu until Start clicked"""
    font = pygame.font.Font(FONT_PATH, 50)
    title_font = pygame.font.Font(FONT_PATH, 80)
    start_btn = pygame.Rect(50, screen.get_height()//2 - 40, 200, 80)
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and start_btn.collidepoint(ev.pos):
                return
        screen.fill(DARK)
        draw_button(screen, start_btn, "Start", font)
        title_surf = title_font.render("ASTEROIDS", True, YELLOW)
        title_rect = title_surf.get_rect(center=(screen.get_width()*3//4, screen.get_height()//2))
        screen.blit(title_surf, title_rect)
        pygame.display.flip()
        clock.tick(30)


def options_screen(screen, clock):
    """Display options and return selections"""
    font = pygame.font.Font(FONT_PATH, 36)
    title_font = pygame.font.Font(FONT_PATH, 60)
    # State
    num_players = 1
    rl_choice = None
    bh_choice = None
    # Layout
    btn_w, btn_h = 150, 50
    x = 50
    # Number of Players
    label_y = 150
    btn_y = label_y + 40
    inc_btn = pygame.Rect(x, btn_y, btn_h, btn_h)
    dec_btn = pygame.Rect(x + btn_h + 20, btn_y, btn_h, btn_h)
    # RL question
    rl_label_y = 260
    rl_btn_y = rl_label_y + 40
    yes_rl = pygame.Rect(x, rl_btn_y, btn_w, btn_h)
    no_rl = pygame.Rect(x + btn_w + 20, rl_btn_y, btn_w, btn_h)
    # BH question
    bh_label_y = 380
    bh_btn_y = bh_label_y + 40
    yes_bh = pygame.Rect(x, bh_btn_y, btn_w, btn_h)
    no_bh = pygame.Rect(x + btn_w + 20, bh_btn_y, btn_w, btn_h)
    # Connect
    connect_btn = pygame.Rect(x, bh_btn_y + 100, 200, 80)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if inc_btn.collidepoint(ev.pos) and num_players < 5:
                    num_players += 1
                if dec_btn.collidepoint(ev.pos) and num_players > 1:
                    num_players -= 1
                if yes_rl.collidepoint(ev.pos): rl_choice = True
                if no_rl.collidepoint(ev.pos): rl_choice = False
                if yes_bh.collidepoint(ev.pos): bh_choice = True
                if no_bh.collidepoint(ev.pos): bh_choice = False
                if connect_btn.collidepoint(ev.pos) and rl_choice is not None and bh_choice is not None:
                    return num_players, rl_choice, bh_choice
        screen.fill(DARK)
        title = title_font.render("ASTEROIDS", True, YELLOW)
        title_rect = title.get_rect(center=(screen.get_width()*3//4, 80))
        screen.blit(title, title_rect)
        # Draw Number of Players
        screen.blit(font.render(f"Number of Players: {num_players}", True, WHITE), (x, label_y))
        draw_button(screen, inc_btn, "+", font)
        draw_button(screen, dec_btn, "-", font)
        # Draw RL question
        screen.blit(font.render("Play as RL Ship?", True, WHITE), (x, rl_label_y))
        # Highlight selection
        draw_button(
            screen, yes_rl, "Yes", font,
            fill_color=YELLOW if rl_choice is True else BLACK,
            text_color=BLACK if rl_choice is True else WHITE
        )
        draw_button(
            screen, no_rl, "No", font,
            fill_color=YELLOW if rl_choice is False else BLACK,
            text_color=BLACK if rl_choice is False else WHITE
        )
        # Draw BH question
        screen.blit(font.render("Growing Blackhole?", True, WHITE), (x, bh_label_y))
        draw_button(
            screen, yes_bh, "Yes", font,
            fill_color=YELLOW if bh_choice is True else BLACK,
            text_color=BLACK if bh_choice is True else WHITE
        )
        draw_button(
            screen, no_bh, "No", font,
            fill_color=YELLOW if bh_choice is False else BLACK,
            text_color=BLACK if bh_choice is False else WHITE
        )
        
        # Draw Connect
        draw_button(screen, connect_btn, "Connect", font)
        pygame.display.flip()
        clock.tick(30)


def main():
    pygame.init()
    WIDTH, HEIGHT = gameParameters.screenWidth, gameParameters.screenHeight
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    menu_screen(screen, clock)
    num_players, rl_choice, bh_choice = options_screen(screen, clock)
    print("Settings:", num_players, rl_choice, bh_choice)

    try:
        net = Network(5) # <-- statically set this to 5 for now, but should be set to the num_players that the FIRST connected lcient 
                        # choses. To do this, the server needs to be able to know which client was the first/have some sort of waiting room aspect though.
        gameParameters.startNumShips = 5
    except RuntimeError as e:
        print("Server refused connection:", e)
        return
    print(f"Connected as player {net.player}")

    gameParameters.enableGrowingBlackhole = bh_choice

    stage = Stage("Asteroids Client", (WIDTH, HEIGHT))
    ships = [Ship(stage, shipIndex=i, color=gameParameters.shipColor[i]) for i in range(gameParameters.startNumShips)]
    for ship in ships:
        stage.addSprite(ship.thrustJet)
        stage.addSprite(ship)
    bh_sprite = Blackhole(stage, gameParameters.screenCenter)
    stage.addSprite(bh_sprite)

    run = True
    while run:
        clock.tick(60)

        # get input from the user
        keys = pygame.key.get_pressed()
        action = 0
        if keys[pygame.K_UP]:    action = 1
        elif keys[pygame.K_LEFT]:  action = 2
        elif keys[pygame.K_RIGHT]: action = 3

        # send action, receive state
        try:
            state = net.send(action)
        except RuntimeError as e:
            print("Connection error:", e)
            break

        # update sprite positions
        for idx, s in enumerate(state['ships']):
            ships[idx].position.x = s['x']
            ships[idx].position.y = s['y']
            ships[idx].angle      = s['angle']

        bh = state['blackhole']
        bh_sprite.position.x = bh['x']
        bh_sprite.position.y = bh['y']

        # draw using full game rendering system
        stage.screen.fill((10, 10, 10))
        stage.moveSprites()
        stage.drawSprites()
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                run = False

    pygame.quit()

if __name__ == "__main__":
    main()
