from multiprocessing import Process
import argparse
import requests
import logging, time
from blockchain import Transaction
from api import app


##this is the way i find to hadel the logger in the consol if you just want to disable it remove every thing and put these two lines
# logger = logging.getLogger("werkzeug")
# logger.disabled = True

# from my understanding about the threading you can use it in loops or something you can set a flag to stop it but things like flask or socket you have to use Process classe so you can terminate the process if you want to

logger = logging.getLogger("werkzeug")
for handler in logger.handlers:
    logger.removeHandler(handler)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
W_handler = logging.FileHandler("file.log")
W_handler.setLevel(logging.WARNING)
W_handler.setFormatter(formatter)
E_handler = logging.FileHandler("file.log")
E_handler.setLevel(logging.ERROR)
E_handler.setFormatter(formatter)
D_handler = logging.FileHandler("file.log")
D_handler.setLevel(logging.DEBUG)
D_handler.setFormatter(formatter)
I_handler = logging.FileHandler("file.log")
I_handler.setLevel(logging.INFO)
I_handler.setFormatter(formatter)
C_handler = logging.FileHandler("file.log")
C_handler.setLevel(logging.INFO)
C_handler.setFormatter(formatter)
logger.addHandler(W_handler)
logger.addHandler(E_handler)
logger.addHandler(D_handler)
logger.addHandler(I_handler)
logger.addHandler(C_handler)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=5500)
    args = parser.parse_args()
    local_api = f"http://127.0.0.1:{args.port}"
    p = Process(
        target=app.run,
        kwargs={
            "host": "0.0.0.0",
            "port": args.port,
            "debug": True,
            "use_reloader": False,
        },
    )
    p.start()
    time.sleep(1)

    while True:
        line = input(">>").strip(" \n").lower()
        line_parts = line.split(" ")

        if line.startswith("send ") and len(line_parts) >= 4:
            host, port, msg = line_parts[1:]
            port = int(port)
            r = requests.post(f"http://{host}:{port}", {"msg": msg})
            print(r)
            print(r.status_code)
            print(r.url)
            print(r.text)

        elif line.startswith("print"):
            r = requests.get(f"{local_api}/get_chain")
            if r.status_code == 200:
                chain = r.json()
                print("\nLength: ", chain["length"])
                print("Blockchain:\n", chain["chain"])
                print("Peers:\n", chain["peers"])

        elif line.startswith("save"):
            r = requests.get(f"{local_api}/save_chain")
            print(r.text)

        # # WHAT IS THIS??????????????????????????
        # elif line.startswith("connect ") and len(line_parts) >= 3:
        #     host, port = line_parts[1:]
        #     r = requests.get(f"http://{host}:{port}/get_chain")
        #     if r.status_code != 200:
        #         raise "error problem with gitting the chain"
        #     chain = json.loads(r.content)
        #     print("***chain has been downloaded")
        #     r = requests.post(f"{local_api}/post_chain", json=chain)
        #     print(r.text)

        elif line.startswith("mine ") and len(line_parts) >= 2:
            miner = line_parts[1]
            r = requests.post(f"{local_api}/mine", json={"miner": miner})
            print(r.text)

        elif line.startswith("peer ") and len(line_parts) >= 3:
            host, port = line_parts[1:]
            r = requests.post(
                f"{local_api}/add_peer", json={"host": host, "port": port}
            )
            print(r.text)

        elif line.startswith("transaction ") and len(line_parts) >= 5:
            # test transaction:
            # transaction 9d0b1e195dde058c70e5faa555243d3022aebd88afc6122411112193540fcff9d656311a7540ee047e733877ca575d827a725b69a56779724ee0c1f41fd7fecc 7239f2dccddf3c01a2aaa7234ea2a6219e3518ecf3313e2c280b801148fbe548 addr2 55
            public_key, private_key, destination, amount = line_parts[1:]
            amount = int(amount)
            tx = Transaction(public_key, destination, amount)
            try:
                tx.sign_transaction(private_key)
            except:
                print("could not sign the transaction")
            r = requests.post(f"{local_api}/add_signed_transaction", json=tx.__str__())
            print(r.text)

        elif line.startswith("quit") or line.startswith("exit"):
            p.terminate()
            p.join()
            return

        elif line.startswith("sync"):
            r = requests.get(f"{local_api}/sync")
            print(r.text)

        else:
            print(
                """Usage: 
    SEND <ip> <port> <msg>
    CONNECT <ip> <port>
    PEER <ip> <port>
    PRINT
    SAVE
    TRANSACTION <public key> <private key> <destination> <amount>
    MINE <miner address>
    QUIT"""
            )


if __name__ == "__main__":
    main()
