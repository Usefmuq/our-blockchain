import hashlib
import time

# import base64
import ecdsa


def ftime():
    return time.strftime("%H:%M:%S %d/%m/%Y", time.localtime())


class Transaction:
    def __init__(self, source=None, to=None, amount=None):
        self.timestamp = ftime()
        self.source = source
        self.to = to
        self.amount = amount
        self.signature = None

    def calc_hash(self):
        return hashlib.sha256(
            f"{self.timestamp}{self.source}{self.to}{self.amount}".encode("utf-8")
        ).digest()

    def sign_transaction(self, key):
        private_key = ecdsa.SigningKey.from_string(
            bytes.fromhex(key), curve=ecdsa.SECP256k1
        )
        if private_key.verifying_key.to_string().hex() != self.source:
            raise "Invalid key"

        txhash = self.calc_hash()
        sig = private_key.sign(txhash)
        # NEED TO encode in DER
        self.signature = sig.hex()

    def validate(self):
        if self.source == None:
            return True
        if not self.signature or len(self.signature) == 0:
            raise "Signature not found"
        public_key = ecdsa.VerifyingKey.from_string(
            bytes.fromhex(self.source), curve=ecdsa.SECP256k1
        )
        return public_key.verify(bytes.fromhex(self.signature), self.calc_hash())

    def from_json(self, json):
        self.timestamp = json["timestamp"]
        self.source = json["source"]
        self.to = json["to"]
        self.amount = json["amount"]
        self.signature = json["signature"]

    def __str__(self):
        return {
            "timestamp": self.timestamp,
            "source": self.source,
            "to": self.to,
            "amount": self.amount,
            "signature": self.signature,
        }


class Block:
    def __init__(self, timestamp=None, transactions=[], prev_hash=""):
        self.nonce = 0
        self.timestamp = timestamp
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.hash = self.calc_hash()

    def calc_hash(self):
        return hashlib.sha256(
            f"{self.timestamp}{self.prev_hash}{[_.__str__() for _ in self.transactions]}{self.nonce}".encode(
                "utf-8"
            )
        ).hexdigest()

    def mine_block(self, difficulty):
        while self.hash[0:difficulty] != f'{"0" * difficulty}':
            self.nonce += 1
            self.hash = self.calc_hash()

    def validate_transactions(self):
        for _ in self.transactions:
            if not _.validate():
                return False
            return True

    def from_json(self, json):
        self.timestamp = json["timestamp"]
        transactions = []
        for _ in json["transactions"]:
            tx = Transaction()
            tx.from_json(_)
            transactions.append(tx)
        self.transactions = transactions
        self.prev_hash = json["prev_hash"]
        self.hash = json["hash"]
        self.nonce = json["nonce"]

    def __str__(self):
        return {
            "timestamp": self.timestamp,
            "transactions": [_.__str__() for _ in self.transactions],
            "prev_hash": self.prev_hash,
            "hash": self.hash,
            "nonce": self.nonce,
        }


class Blockchain:
    def __init__(self):
        self.difficulty = 2
        self.chain = [self.create_genesis()]
        self.pending_transactions = []
        self.mining_reward = 100

    def create_genesis(self):
        genesis = Block(ftime(), [])
        genesis.mine_block(self.difficulty)
        return genesis

    def latest_block(self):
        return self.chain[-1]

    def mine_pending_transactions(self, reward_address):
        block = Block(ftime(), self.pending_transactions)
        block.prev_hash = self.latest_block().hash
        block.mine_block(self.difficulty)
        self.chain.append(block)

        self.pending_transactions = [
            Transaction(None, reward_address, self.mining_reward)
        ]

    # REVIEW this later
    def add_transaction(self, transaction):
        if not transaction.source or not transaction.to:
            raise "No source or to address"
        if not transaction.validate():
            raise "Can't add invalid transaction"
        if transaction.amount <= 0:
            raise ValueError
        # check if the sender has the amount on his wallet
        # if self.get_balance_of_address(transaction.source) < transaction.amount:
        #     raise ValueError
        self.pending_transactions.append(transaction)

    def get_balance_of_address(self, address):
        balance = 0
        for block in self.chain:
            for trans in block.transactions:
                if trans.source == address:
                    balance -= trans.amount
                if trans.to == address:
                    balance += trans.amount
        return balance

    def get_history_of_address(self, address):
        history = []
        for block in self.chain:
            for trans in block.transactions:
                if trans.source == address or trans.to == address:
                    history.append(trans)
        return history

    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            prev_block = self.chain[i - 1]
            if not current_block.validate_transactions():
                return False
            # FIX THIS current_block.calc_hash() returns wrong hash
            # ^ was this fixed?????????????
            if current_block.hash != current_block.calc_hash():
                return False
            if current_block.prev_hash != prev_block.hash:
                return False
        return True

    def add_block(self, block):
        if not block.validate_transactions():
            return False
        if block.hash != block.calc_hash():
            return False
        if block.prev_hash != self.latest_block().hash:
            return False
        self.chain.append(block)
        return True

    def from_json(self, json):
        chain = []
        for _ in json:
            block = Block()
            block.from_json(_)
            chain.append(block)
        self.chain = chain

    def __str__(self):
        ret = []
        for block in self.chain:
            ret.append(block.__str__())
        return ret
