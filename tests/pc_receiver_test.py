import socket
import struct
import cv2
import numpy as np

HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print("En attente de connexion du NAO...")
conn, addr = server_socket.accept()
print("Connecté à :", addr)

data_buffer = b''

try:
    while True:
        # Lire taille image
        while len(data_buffer) < 4:
            data_buffer += conn.recv(4096)

        packed_size = data_buffer[:4]
        data_buffer = data_buffer[4:]
        msg_size = struct.unpack(">L", packed_size)[0]

        # Lire image complète
        while len(data_buffer) < msg_size:
            data_buffer += conn.recv(4096)

        img_data = data_buffer[:msg_size]
        data_buffer = data_buffer[msg_size:]

        # Décoder image
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        cv2.imshow("Flux NAO", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    conn.close()
    server_socket.close()
    cv2.destroyAllWindows()
