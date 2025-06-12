import socket
import _thread
import pickle
from game import Game

MAX_PLAYERS = 3
games = {}
id_count = 0

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
s.bind(("0.0.0.0", 5600))
s.listen(MAX_PLAYERS)
print(f"Server started on {"127.0.0.1"}:{5600}")

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
    p = (id_count - 1) % 5 # <--- TODO: need to be able to update this number dynamically based on num_players selected by the first user
    game_id = (id_count - 1) // 5

    if id_count % 5 == 1:
        # first player creates the game
        # games[game_id] = Game(game_id)
        # print("Created new game", game_id)

        raw = conn.recv(265).decode()
        print(f"[Server] raw num_players from client: {raw!r}")

        try: 
            import gameParameters
            n = int(raw)
            gameParameters.startNumShips = 5 # <--- statically set to 5 for now
            games[game_id] = Game(game_id)
            # override and rebuild the ship list:
            games[game_id].env.startNumShips = 5
            games[game_id].env.initialiseGame()
        except ValueError:
            games[game_id] = Game(game_id)
            print("Invalid Number of Players selected from client, using default of 4.")
       
        print("Created new game", game_id)
    else:
        # second player marks it ready
        games[game_id].ready = True
        print("Game", game_id, "ready")

    # _thread.start_new_thread(function, args[, kwargs])
    # Start a new thread and return its identifier.
    _thread.start_new_thread(threaded_client, (conn, p, game_id))
