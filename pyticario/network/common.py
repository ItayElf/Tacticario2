
HEADER = 6
DELIMITER = '~'


def send(soc, msg):
    msg_len = str(len(msg)).zfill(HEADER).encode()
    soc.send(msg_len + msg.encode())


def receive(soc):
    length = soc.recv(HEADER)
    if length:
        length = int(length)
        return soc.recv(length).decode()
    return ''


def parse(msg):
    cmd = msg.split(DELIMITER)[0]
    params = msg.split(DELIMITER)[1:]
    return cmd, params
