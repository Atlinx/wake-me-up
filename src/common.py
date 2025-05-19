import socket
import msgpack
import msg
from typing import Callable, Union
from colored import Fore, Back, Style


CYAN_BOLD = Fore.cyan + Style.bold
GREEN_BOLD = Fore.green + Style.bold
RED_BOLD = Fore.red + Style.bold
RESET = Style.reset


def exiterr(msg):
    print(f"{RED_BOLD}ERROR: {RESET}{msg}")
    exit(1)


MESSAGE_SIZE_HEADER_BYTES = 4
RECV_MSG_FN = Callable[[], None]
SEND_MSG_FN = Callable[[msg.MsgID, dict], None]
MAIN_CONN_FN = Callable[[socket.socket, str, RECV_MSG_FN, SEND_MSG_FN], None]


def handle_conn(
    conn: socket.socket,
    addr: str,
    main_fn: MAIN_CONN_FN,
):
    """Handles a socket connection

    Args:
        conn (socket.socket): The socket connection
        addr (str): Address that created this connection
    """

    def recv_n(n: int) -> Union[bytes, None]:
        """Receives exactly n bytes from the socket.

        Args:
            n (int): Number of bytes to read from the socket

        Returns:
            bytes: The received content in bytes
        """
        data = bytearray()
        while len(data) < n:
            packet = conn.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)

    msg_size = 0

    def recv_msg() -> Union[tuple[msg.MsgID, dict], None]:
        nonlocal msg_size
        msg_size_raw = recv_n(MESSAGE_SIZE_HEADER_BYTES)
        if msg_size_raw == None:
            return None
        msg_size = int.from_bytes(
            msg_size_raw,
            byteorder="big",
            signed=False,
        )
        msg_buf = recv_n(msg_size)
        id = msg.MsgID(msg_buf[0])
        resp = msgpack.unpackb(msg_buf[1:])
        return (id, resp)

    def send_msg(id: msg.MsgID, body):
        """
        Sends a msg with an ID and body
        The msg is encoded using msgpack

        Args:
            id (msg.MsgID): ID of the msg
            body (_type_): Content of the msg
        """
        buf = bytearray()
        packed_body: bytes = msgpack.packb(msg.to_dict(body))
        send_msg_size = len(packed_body) + 1  # +1 to include id
        buf.extend(
            send_msg_size.to_bytes(
                length=MESSAGE_SIZE_HEADER_BYTES,
                byteorder="big",
                signed=False,
            )
        )
        buf.extend(id.value.to_bytes(length=1, byteorder="big", signed=False))
        buf.extend(packed_body)
        conn.sendall(buf)

    main_fn(conn, addr, recv_msg, send_msg)
