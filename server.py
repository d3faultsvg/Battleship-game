import socket
import threading
import json
import time
from game_logic import check_hit, all_ships_sunk, is_ship_sunk

HOST = '0.0.0.0'
PORT = 5555

clients = [None, None]
boards = [None, None]
ships = [None, None]
turn = 0


def send_json(conn, obj):
    message = json.dumps(obj) + "\n"
    conn.sendall(message.encode())

def handle_client(conn, player_id):
    global turn
    try:
        data = conn.recv(8192).decode()
        parsed = json.loads(data)
        print(f"parsed: {parsed}")

        boards[player_id] = parsed['board']
        ships[player_id] = parsed['ships']
        clients[player_id] = conn
        print(f"[SERVER] Plansza i statki odebrane od gracza {player_id}.")

        while not all(boards):
            time.sleep(0.1)

        if player_id == 0:
            for pid in (0, 1):
                send_json(clients[pid], {"msg": "Gra się rozpoczęła!"})
                if pid == 0:
                    send_json(clients[pid], {"msg": "Twoja tura"})
                else:
                    send_json(clients[pid], {"msg": "Tura przeciwnika"})

        game_over = False
        while not game_over:
            if turn != player_id:
                time.sleep(0.1)
                continue

            try:
                shot_data = conn.recv(1024).decode()
                if not shot_data.strip():
                    break
                shot = json.loads(shot_data)
                x, y = shot["x"], shot["y"]

                print(f"[SERVER] Gracz {player_id} strzela w ({x}, {y})")

                hit = check_hit(boards[1 - player_id], x, y)
                if hit:
                    if is_ship_sunk(ships[1 - player_id], boards[1 - player_id], x, y):
                        result = "trafiony zatopiony"
                    else:
                        result = "trafiony"
                else:
                    result = "pudło"

                send_json(conn, {"msg": result, "x": x, "y": y})
                send_json(clients[1 - player_id], {
                    "msg": f"{result.capitalize()} w ({x}, {y})",
                    "hit": hit,
                    "x": x,
                    "y": y
                })

                if all_ships_sunk(boards[1 - player_id]):
                    print(f"[SERVER] Gracz {player_id} wygrał!")
                    send_json(conn, {"msg": "Wygrałeś!", "x": x, "y": y})
                    send_json(clients[1 - player_id], {"msg": "Przegrałeś.", "x": x, "y": y})
                    game_over = True
                    continue

                turn = 1 - player_id
                send_json(clients[turn], {"msg": "Twoja tura"})
                send_json(clients[player_id], {"msg": f"{result.capitalize()}! Tura przeciwnika"})

            except Exception as e:
                print(f"[SERVER] Błąd podczas strzału: {e}")
                break

    except Exception as e:
        print(f"[SERVER] Błąd połączenia z graczem {player_id}: {e}")
    finally:
        conn.close()
        print(f"[SERVER] Gracz {player_id} rozłączony.")

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print(f"[SERVER] Serwer działa na {HOST}:{PORT}")

    player_id = 0
    while player_id < 2:
        conn, addr = server.accept()
        print(f"[SERVER] Gracz {player_id} połączony z {addr}")
        thread = threading.Thread(target=handle_client, args=(conn, player_id))
        thread.start()
        player_id += 1

if __name__ == "__main__":
    start()
