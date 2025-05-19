import socket
import os
import ssl
import argparse
from dotenv import load_dotenv
import json
import msg
import common as cmn


def handle_conn(
    conn: socket.socket,
    addr: str,
    recv_msg: cmn.RECV_MSG_FN,
    send_msg: cmn.SEND_MSG_FN,
    args: dict,
):
    print(f"{cmn.GREEN_BOLD}Connected... ✅")
    print(f"    Socket info: {conn.version()}{cmn.RESET}")
    send_msg(msg.MsgID.AUTH, args.password)
    resp = recv_msg()
    print(f"{resp[1]}")
    if resp[1] != "Authenticated":
        conn.close()
        return
    match args.cmd:
        case "wake":
            print(f"Waking: {args.name}")
            send_msg(msg.MsgID.WAKEUP, args.name)
            resp = recv_msg()
            print(f"{resp[1]}")
        case "list":
            send_msg(msg.MsgID.LIST, {})
            resp = recv_msg()
            print(f"Available names")
            print(f"{json.dumps(resp[1], indent=4)}")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="client.py",
        description="Communicates with server to request wakeups.",
    )
    parser.add_argument(
        "-a",
        "--address",
        default=os.environ.get("HOST", "127.0.0.1"),
        type=str,
        help="Host to connect to.",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=os.environ.get("PORT", 8753),
        type=int,
        help="Port on the host to connect to.",
    )
    parser.add_argument(
        "-c",
        "--cert",
        default=os.environ.get("CERT", "./host.cert"),
        type=str,
        help="Path to the .cert file.",
    )
    parser.add_argument(
        "-w",
        "--password",
        default=os.environ.get("PASSWORD", ""),
        type=str,
        help="Password to authenticate with the server.",
    )
    subparsers = parser.add_subparsers(required=True, dest="cmd")

    # Parse list command
    parser_list = subparsers.add_parser(
        "list", help="Lists available computers to wake up."
    )

    # Parse list command
    parser_wake = subparsers.add_parser("wake", help="Wakes up a computer.")
    parser_wake.add_argument("name", type=str, help="Name of computer to wake up.")

    args = parser.parse_args()

    print(f"{cmn.GREEN_BOLD}Client started... 🚀{cmn.RESET}")
    print(f"{json.dumps(args.__dict__, indent=4)}")

    # Create an SSL socket...
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(args.cert)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        with context.wrap_socket(sock, server_hostname=args.address) as ssock:

            def handle_conn_(
                conn: socket.socket,
                addr: str,
                recv_msg: cmn.RECV_MSG_FN,
                send_msg: cmn.SEND_MSG_FN,
            ):
                handle_conn(conn, addr, recv_msg, send_msg, args)

            ssock.connect((args.address, args.port))
            cmn.handle_conn(ssock, args.address, handle_conn_)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        raise e
        cmn.exiterr(e)
