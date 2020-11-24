from flask import Flask, request, jsonify
from blockchain import Blockchain, Block, Transaction
import requests
import pickle
import json


def load():
    try:
        with open("blockchain.dat", "rb") as file:
            chain = pickle.load(file)
        return chain
    except FileNotFoundError:
        print("Did not load")


def save(chain):
    with open("blockchain.dat", "wb") as file:
        pickle.dump(chain, file, pickle.HIGHEST_PROTOCOL)


def is_request_local():
    if request.remote_addr == "127.0.0.1":
        return True


chain = load()
peers = []
app = Flask(__name__)


@app.route("/", methods=["GET"])
@app.route("/get_chain", methods=["GET"])
def index():

    return jsonify(
        {"peers": peers, "length": len(chain.chain), "chain": chain.__str__()}
    )


# this shouldn't be used anyway, need to automatically save every time there are changes
@app.route("/save_chain", methods=["GET"])
def save_chain():
    if not is_request_local():
        return "Forbidden", 403
    try:
        save(chain)
    except:
        return "Error occured", 500
    return "Success", 200


@app.route("/mine", methods=["POST"])
def mine():
    if not is_request_local():
        return "Forbidden", 403
    sigs = [_.signature for _ in chain.pending_transactions]
    for peer in peers:
        print(f"\tconnecting to http://{peer}/pending_transactions")
        r = requests.get(f"http://{peer}/pending_transactions").json()
        for _ in r:
            tx = Transaction()
            tx.from_json(_)
            if tx.signature not in sigs:
                chain.pending_transactions.append(tx)
                sigs.append(tx.signature)
    if not chain.pending_transactions:
        return "\t\tFailed there is no transactions to mine", 404
    else:
        mine_data = request.get_json()
        try:
            chain.mine_pending_transactions(mine_data["miner"])
            # if it does not work later try request.environ['REMOTE_ADDR'] & request.environ['REMOTE_PORT']
            r = requests.get(f"http://{request.environ['HTTP_HOST']}/announce_block")
            print(r.text)
            return "Success block has been mined", 201
        except:
            return "Failed could not mine the block", 404


@app.route("/pending_transactions", methods=["GET"])
def pending_transactions():
    return jsonify([_.__str__() for _ in chain.pending_transactions])


@app.route("/announce_block", methods=["GET"])
def announce_block():
    counter = 0
    block = chain.latest_block()
    for peer in peers:
        try:
            print(f"\tAnnouncing to {peer}")
            r = requests.post(f"http://{peer}/add_block", json=block.__str__())
            print(r.text)
            counter += 1
        except:
            print(f"\t\tFailed to connect with {peer}")
    return f"Block was announced to {counter} peers"


# maybe we need to check if the incoming block is from a chain of the same length or not?
@app.route("/add_block", methods=["POST"])
def add_block():
    try:
        block = Block()
        block.from_json(request.get_json())
        chain.add_block(block)
    except:
        return "Error occured when adding announced block", 500
    return "Success when adding announced block", 200


@app.route("/add_signed_transaction", methods=["POST"])
def add_signed_transaction():
    tx = Transaction()
    tx.from_json(request.get_json())
    try:
        chain.add_transaction(tx)
    except:
        return "Failed could not add transaction", 404
    return "Success transaction", 201


# # WHAT IS THIS???
# @app.route("/post_chain", methods=["POST"])
# def post_chain():
#     post_data = request.get_json()
#     temp_chain = Blockchain()
#     temp_chain.from_json(post_data["chain"])
#     if temp_chain.validate_chain():
#         save(temp_chain)
#         global chain
#         global peers
#         chain = load()
#         peers = []
#         for _ in post_data["peers"]:
#             if _ not in peers:
#                 peers.append(_)
#         return (
#             f"Success chain saved {len(temp_chain.chain)} blocks and {len(peers)} peers was added",
#             201,
#         )
#     return "Failed could not saved chain", 404


@app.route("/add_peer", methods=["POST"])
def add_peer():
    try:
        global peers
        peer_data = request.get_json()
        peer = f"{peer_data['host']}:{peer_data['port']}"
        if peer in peers:
            raise "peer already added"
        else:
            peers.append(peer)
            return "Success peer added", 201
    except:
        return "Failed could not add peer", 404


@app.route("/sync", methods=["GET"])
def sync():
    if not is_request_local():
        return "Forbidden", 403
    global chain
    longest_chain = None
    current_len = len(chain.chain)
    for peer in peers:
        print(f"Connecting to http://{peer}")
        try:
            r = requests.get(f"http://{peer}").json()
        except:
            print(f"Could not connect to http://{peer}")
            continue
        if r["length"] > current_len:
            current_len = r["length"]
            temp_chain = Blockchain()
            temp_chain.from_json(r["chain"])
            if temp_chain.validate_chain():
                longest_chain = temp_chain
            else:
                print(f"Chain from {peer} is fabricated")
    if longest_chain:
        chain = longest_chain
    return "Blockchain synced", 200
