import socket
import os
import ssl
import argparse
from colored import Fore, Back, Style
from dotenv import load_dotenv
import wakeonlan
import json
import msgpack
import msg
import common as cmn


def handle_conn(
    conn: socket.socket,
    addr: str,
    recv_msg: cmn.RECV_MSG_FN,
    send_msg: cmn.SEND_MSG_FN,
    config: dict,
):
    print(f"{cmn.GREEN_BOLD}Client connected @ {addr}{cmn.RESET}")
    authenticated = False
    while True:
        res = recv_msg()
        if res == None:
            break
        id, data = res
        if not authenticated:
            if id == msg.MsgID.AUTH:
                password = data
                if password == os.environ.get("PASSWORD"):
                    authenticated = True
                    send_msg(msg.MsgID.RESULT, "Authenticated")
                else:
                    send_msg(msg.MsgID.RESULT, "Unauthenticated")
            else:
                send_msg(msg.MsgID.RESULT, "Unauthenticated")
                conn.close()
        else:
            match id:
                case msg.MsgID.WAKEUP:
                    name = data
                    if name in config["computers"]:
                        computer_data = config["computers"][name]
                        print(f"send magic packet to {computer_data['mac']}")
                        wakeonlan.send_magic_packet(
                            computer_data["mac"], ip_address=computer_data["ip"]
                        )
                        send_msg(msg.MsgID.RESULT, f"Sent wakeup packet to '{name}'.")
                    else:
                        send_msg(msg.MsgID.RESULT, "Invalid name.")
                case msg.MsgID.LIST:
                    send_msg(msg.MsgID.RESULT, config["computers"].keys())
                case _:
                    send_msg(msg.MsgID.RESULT, "Unknown command.")
        print(f"    Received msg: {id} response: {data}")
    print(f"    Client disconnected @ {addr}")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog=f"server.py",
        description="Handles requests for wakeups",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=os.environ.get("PORT", 8753),
        type=int,
        help="Port to host the server on.",
    )
    parser.add_argument(
        "-c",
        "--cert",
        default=os.environ.get("CERT", "./host.cert"),
        type=str,
        help="Path to the .cert file.",
    )
    parser.add_argument(
        "-k",
        "--key",
        default=os.environ.get("KEY", "./host.key"),
        type=str,
        help="Path to the .key file.",
    )
    parser.add_argument(
        "-g",
        "--config",
        default=os.environ.get("CONFIG", "./config.json"),
        type=str,
        help="Path to the config JSON file.",
    )
    args = parser.parse_args()

    config: dict = {}
    try:
        with open(args.config, "r") as file:
            config = json.load(file)
    except Exception as e:
        cmn.exiterr(f"Failed to open config.json file: {e}")

    print(f"{cmn.GREEN_BOLD}Server started... 🚀{cmn.RESET}")
    print(f"Args:   {json.dumps(args.__dict__, indent=4)}")
    print(f"Config: {json.dumps(config, indent=4)}")

    # Create an SSL socket...
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(args.cert, args.key)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind(("127.0.0.1", args.port))
        sock.listen()
        sock.settimeout(0.2)
        with context.wrap_socket(sock, server_side=True) as ssock:
            try:
                while True:
                    try:

                        def handle_conn_(
                            conn: socket.socket,
                            addr: str,
                            recv_msg: cmn.RECV_MSG_FN,
                            send_msg: cmn.SEND_MSG_FN,
                        ):
                            handle_conn(conn, addr, recv_msg, send_msg, config)

                        conn, addr = ssock.accept()
                        cmn.handle_conn(conn, addr, handle_conn_)
                    except socket.timeout:
                        pass
            except KeyboardInterrupt:
                print("Exiting...")
                exit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        raise e
        exiterr(e)
