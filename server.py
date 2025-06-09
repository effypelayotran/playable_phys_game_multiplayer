import socket
import _thread
import pickle
from game import Game

MAX_PLAYERS = 3
games = {}
id_count = 0

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
s.bind(("0.0.0.0", 5500))
s.listen(MAX_PLAYERS)
print(f"Server started on {"0.0.0.0"}:{5500}")

def threaded_client(conn, p, game_id):
    global id_count
    conn.sendall(str(p).encode())  # send player number

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            game = games[game_id]
           
            if data != "get":  # if it's an action (not "get"), apply it
                game.play(p, int(data))

            game.step()                 # step the world once
            state = game.get_state()    # then send back the current state
            conn.sendall(pickle.dumps(state))

        except Exception as e:
            print(f"Client {p} disconnected:", e)
            break

    conn.close()
    del games[game_id]
    id_count -= 1
    print(f"Closed connection for player {p}")

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    id_count += 1
    p = (id_count - 1) % 2
    game_id = (id_count - 1) // 2

    if id_count % 2 == 1:
        # first player creates the game
        games[game_id] = Game(game_id)
        print("Created new game", game_id)
    else:
        # second player marks it ready
        games[game_id].ready = True
        print("Game", game_id, "ready")

    # _thread.start_new_thread(function, args[, kwargs])
    # Start a new thread and return its identifier.
    _thread.start_new_thread(threaded_client, (conn, p, game_id))
