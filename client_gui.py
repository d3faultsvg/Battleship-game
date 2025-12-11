import pygame
import socket
import threading
import json
from game_logic import create_empty_board, place_ship, can_place_ship

CELL_SIZE = 30
MARGIN = 20
BOARD_SIZE = 10
SCREEN_WIDTH = CELL_SIZE * BOARD_SIZE * 2 + MARGIN * 3
SCREEN_HEIGHT = CELL_SIZE * BOARD_SIZE + MARGIN * 3 + 30
SHIP_SIZES = [5, 4, 3, 3, 2]

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
WHITE_HIT = (220, 220, 220)

HOST = "172.20.10.5"
PORT = 5555


def draw_board(screen, board, offset_x, offset_y):
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            cell = board[y][x]
            color = BLUE
            if cell == "S":
                color = GRAY
            elif cell == "X":
                color = RED
            elif cell == "O":
                color = WHITE_HIT
            pygame.draw.rect(screen, color, (offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, BLACK, (offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)


def draw_text(screen, text, font, x, y):
    label = font.render(text, True, BLACK)
    screen.blit(label, (x, y))


def recv_thread(file, opponent_board, set_info, update_player_board):
    global my_turn, game_over
    while True:
        try:
            line = file.readline()
            if not line:
                break
            response = json.loads(line.strip())
            print("[KLIENT] Odebrano:", response)

            msg = response.get("msg")
            x = response.get("x")
            y = response.get("y")

            if msg:
                if msg == "Twoja tura":
                    my_turn = True
                    set_info("Twoja tura")
                elif msg == "Tura przeciwnika":
                    my_turn = False
                    set_info("Tura przeciwnika")
                elif msg == "trafiony":
                    opponent_board[y][x] = "X"
                    set_info("Trafiony!")
                elif msg == "trafiony zatopiony":
                    opponent_board[y][x] = "X"
                    set_info("Trafiony zatopiony!")
                elif msg == "pudło":
                    opponent_board[y][x] = "O"
                    set_info("Pudło")
                elif msg == "Wygrałeś!":
                    opponent_board[y][x] = "X"
                    set_info("Wygrałeś!")
                    game_over = True
                elif msg == "Przegrałeś.":
                    opponent_board[y][x] = "X"
                    set_info("Przegrałeś...")
                    game_over = True
                elif msg.startswith("Gra się rozpoczęła") or msg.startswith("Wszystkie statki"):
                    set_info(msg)
        except Exception as e:
            set_info(f"Błąd odbioru: {e}")
            break


def connect_and_send_board(player_board, ships, set_info, update_player_board, opponent_board):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    data = {"board": player_board, "ships": ships}
    client_socket.sendall((json.dumps(data) + "\n").encode())

    file = client_socket.makefile("r")
    threading.Thread(target=recv_thread, args=(file, opponent_board, set_info, update_player_board), daemon=True).start()

    return client_socket


def main():
    global my_turn, game_over

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Statki - Gracz")
    font = pygame.font.SysFont(None, 24)

    player_board = create_empty_board()
    opponent_board = create_empty_board()
    ships = []

    current_ship_index = 0
    direction = "H"
    placing_mode = True
    info = f"Rozmieść statki | Rozmiar: {SHIP_SIZES[current_ship_index]} | Kierunek: {direction}"

    client_socket = None
    my_turn = False
    game_over = False

    def set_info(msg):
        nonlocal info
        info = msg

    def update_player_board(x, y, value):
        player_board[y][x] = value

    clock = pygame.time.Clock()

    while True:
        screen.fill(WHITE)
        draw_board(screen, player_board, MARGIN, MARGIN)
        draw_board(screen, opponent_board, MARGIN * 2 + BOARD_SIZE * CELL_SIZE, MARGIN)

        draw_text(screen, "Twoja plansza", font, MARGIN, MARGIN - 20)
        draw_text(screen, "Plansza przeciwnika", font, MARGIN * 2 + BOARD_SIZE * CELL_SIZE, MARGIN - 20)
        draw_text(screen, info, font, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 30)

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            elif event.type == pygame.KEYDOWN and placing_mode:
                if event.key == pygame.K_r:
                    direction = "V" if direction == "H" else "H"
                    info = f"Rozmieść statki | Rozmiar: {SHIP_SIZES[current_ship_index]} | Kierunek: {direction}"

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                grid_x = (x - MARGIN) // CELL_SIZE
                grid_y = (y - MARGIN) // CELL_SIZE

                if placing_mode:
                    if 0 <= grid_x < BOARD_SIZE and 0 <= grid_y < BOARD_SIZE:
                        size = SHIP_SIZES[current_ship_index]
                        if can_place_ship(player_board, grid_x, grid_y, size, direction):
                            ship_coords = place_ship(player_board, grid_x, grid_y, size, direction)
                            ships.append(ship_coords)
                            current_ship_index += 1
                            if current_ship_index >= len(SHIP_SIZES):
                                placing_mode = False
                                info = "Wszystkie statki rozmieszczone – czekaj na przeciwnika..."
                                pygame.time.delay(100)
                                client_socket = connect_and_send_board(player_board, ships, set_info, update_player_board, opponent_board)
                            else:
                                info = f"Rozmieść statki | Rozmiar: {SHIP_SIZES[current_ship_index]} | Kierunek: {direction}"
                else:
                    if my_turn and not game_over:
                        ox = (MARGIN * 2 + BOARD_SIZE * CELL_SIZE)
                        oy = MARGIN
                        grid_x = (x - ox) // CELL_SIZE
                        grid_y = (y - oy) // CELL_SIZE
                        if 0 <= grid_x < BOARD_SIZE and 0 <= grid_y < BOARD_SIZE:
                            if opponent_board[grid_y][grid_x] == "~":
                                shot = {"x": grid_x, "y": grid_y}
                                client_socket.sendall((json.dumps(shot) + "\n").encode())
                                my_turn = False
                                set_info("Czekaj na odpowiedź przeciwnika...")

if __name__ == "__main__":
    main()