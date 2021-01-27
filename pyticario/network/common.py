import time

HEADER = 6
DELIMITER = '~'


def send(soc, msg):
    msg_len = str(len(msg)).zfill(HEADER).encode()
    soc.send(msg_len + msg.encode())


def receive(soc):
    length = soc.recv(HEADER)
    if length:
        length = int(length)
        if length < 1000:
            return soc.recv(length).decode()
        index = 0
        msg = ''
        while index <= length:
            msg += soc.recv(1000).decode()
            index += 1000
            time.sleep(0.05)
        return msg
    return ''


def parse(msg):
    cmd = msg.split(DELIMITER)[0]
    params = msg.split(DELIMITER)[1:]
    return cmd, params
