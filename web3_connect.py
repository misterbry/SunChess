from time import sleep
import os
from web3 import Web3
import json
from dotenv import load_dotenv, set_key
from getpass import getpass
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
from User import User
import utils
import menu

load_dotenv()
env_path = ".env"
os.system("clear")

# Connect to polygon
public_node = os.getenv("AMOY_NODE")
contract_address = os.getenv("CONTRACT_ADDRESS")
dev_address = os.getenv("DEV_ADDRESS")
snac_address = os.getenv("SNAC_ADDRESS")
account = None
dev_key = os.getenv("PRIVATE_KEY")
w3 = Web3(Web3.HTTPProvider(public_node))
dev_account = w3.eth.account.from_key(dev_key)

if w3.is_connected:
    print("You are connected to the blockchain.")
    print("Chain ID:", w3.eth.chain_id)
else:
    print("Connection error, exiting...")
    sleep(2)
    exit()

sleep(2)
os.system('clear')

with open("artifacts/contracts/SunChess.sol/SunChess.json") as f:
    data = json.load(f)
    abi = data["abi"]
    f.close()

with open("artifacts/contracts/SunsetNeighborhoodAltCoin.sol/SunsetNeighborhoodAltCoin.json") as f:
    data = json.load(f)
    snac_abi = data["abi"]
    f.close()
    
contract = w3.eth.contract(address=contract_address, abi=abi)
snac_contract = w3.eth.contract(address=snac_address, abi=snac_abi)
owner = contract.functions.owner().call()
message = contract.functions.message().call()

# Retrieve the encrypted wallet and salt from the .env file
def initial_setup(key, value):
    set_key(env_path, key, value)
    
users = {}
returning_user = None
username = input("Enter your username >>> ")

def splash():
    try:
        users = utils.load_users()
        # print(users)
        returning_user = users[username]
        print(returning_user.address)
        initial_setup("WALLET_SALT", returning_user.salt)
        initial_setup("ENCRYPTED_WALLET", returning_user.wallet)
        initial_setup("USER_ADDRESS", returning_user.address)
        return returning_user
    except Exception:
        new_user = noob()
        return new_user

def returning(a, w, s):
    print("Success retrieving wallet!")
    sleep(2)
    load_dotenv()
    # encrypted_wallet_base64 = os.getenv('ENCRYPTED_WALLET')
    # wallet_salt_base64 = os.getenv('WALLET_SALT')
    # user_address = os.getenv('USER_ADDRESS')
    encrypted_wallet_base64 = w
    wallet_salt_base64 = s
    user_address = a    
    encrypted_wallet = base64.b64decode(encrypted_wallet_base64)
    salt = base64.b64decode(wallet_salt_base64)
    # Collect user input for the password
    password = getpass("Enter your password to decrypt your wallet >>> ")

    # Derive the key using the provided password and the stored salt
    key = derive_key(password, salt)

    # Decrypt the wallet
    try:
        private_key_hex = decrypt_wallet(key, encrypted_wallet)
        # web3 = Web3()
        global account
        account = w3.eth.account.from_key(private_key_hex)
        if account.address == user_address:
            balance = w3.eth.get_balance(account.address)
            print(message)
            print(f"Your balance is {w3.from_wei(balance, 'ether')} MATIC")

    except Exception as e:
        print("Failed to decrypt the wallet. Please check your password and try again.")
        returning(a, w, s)

    player = menu.main(w3, account, contract)
    if player != 0:
        print("Good to go, have fun!")
        sleep(2)
        return (account, player)
    else:
        if player == 0:
            requests = contract.functions.getRequests().call({
                "from": dev_address
            })
            # print("REQUESTS:", requests)
            approval = bool(input(f"Are you ready to join {requests[0][0]}? "))
            approve_receipt = menu.contract_tx(w3, dev_account, contract, "approvePlayer", (0, approval))
            if approval:
                tx_receipt = transfer_coin(w3, dev_account, account.address, 0.25)
                print("Welcome to the future. You have just received 0.25 complimentary MATIC.")
                sleep(2)
                player = execute()
                return player
            else:
                print("Player denied.")
                sleep(2)
                exit()
        else:
            return 1

    
    # print("Transaction completed at", tx_receipt[0])
    # dev_snac_bal = snac_contract.functions.balanceOf(dev_account.address).call()
    # print("DEV SNACS BEFORE:", dev_snac_bal)
    # tx_receipt = menu.contract_tx(w3, dev_account, snac_contract, "transfer", (account.address, 1))
    # print("Transaction completed at", tx_receipt[0])
    # snac_bal = snac_contract.functions.balanceOf(account.address).call()
    # print("USER SNACS:", snac_bal)
    # dev_snac_bal = snac_contract.functions.balanceOf(dev_account.address).call()
    # print("DEV SNACS AFTER:", dev_snac_bal)

def transfer_coin(w3, account, to, value):
    addr = account.address
    pk = account.key.hex()
    gas_estimate = w3.eth.estimate_gas({
        "from": addr,
        "to": to,
        "value": w3.to_wei(value, "ether")
    }),
    gas_price = w3.eth.gas_price
    tx = {
        "from": addr,
        "to": to,
        "value": w3.to_wei(value, "ether"),
        "nonce": w3.eth.get_transaction_count(addr),
        "gas": gas_estimate[0],
        "gasPrice": gas_price,
        "chainId": w3.eth.chain_id
    }
    sig_tx = w3.eth.account.sign_transaction(tx, pk)
    tx_hash = w3.eth.send_raw_transaction(sig_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return (tx_hash.hex(), tx_receipt)

# Derive a key from the password using Scrypt
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return key

# contract_name = contract.functions.name().call()
# print(f"You are interacting with the {contract_name} contract")

# Derive a key from the password using Scrypt
def derive_key(password: str, salt: bytes) -> bytes:
   kdf = Scrypt(
       salt=salt,
       length=32,
       n=2**14,
       r=8,
       p=1,
       backend=default_backend()
   )
   key = kdf.derive(password.encode())
   return key

# Encrypt the wallet using the derived key
def encrypt_wallet(key: bytes, wallet_data: str) -> bytes:
   iv = os.urandom(16)
   cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
   encryptor = cipher.encryptor()
   encrypted_wallet = iv + encryptor.update(wallet_data.encode()) + encryptor.finalize()
   return encrypted_wallet

# Decrypt the wallet using the derived key
def decrypt_wallet(key: bytes, encrypted_wallet: bytes) -> str:
   iv = encrypted_wallet[:16]
   encrypted_data = encrypted_wallet[16:]
   cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
   decryptor = cipher.decryptor()
   decrypted_wallet = decryptor.update(encrypted_data) + decryptor.finalize()
   return decrypted_wallet.decode()

def noob():
    # Collect user input
    username = input("Welcome simple human. We detect that you are in an unevolved state. Please enter a username to evolve >>> ")
    password = getpass("Please enter a password to access your wallet later >>> ")

    # Generate a salt and derive a key from the password
    salt = os.urandom(16)
    key = derive_key(password, salt)

    # Create a new Ethereum wallet
    web3 = Web3()
    account = web3.eth.account.create()
    wallet_data = account._private_key.hex()

    # Encrypt the wallet
    encrypted_wallet = encrypt_wallet(key, wallet_data)

    # Save the salt and encrypted wallet to the .env file
    salt = base64.b64encode(salt).decode('utf-8')
    wallet = base64.b64encode(encrypted_wallet).decode('utf-8')
    initial_setup("WALLET_SALT", salt)
    initial_setup("ENCRYPTED_WALLET", wallet)
    initial_setup("USER_ADDRESS", account.address)
    print(f"Welcome aboard. Your new address is {account.address}.")
    if utils.data_exists():
        global users
        users = utils.load_users()
    new_user = User(account.address, wallet, salt)
    users[username] = new_user
    utils.save(users)
    return new_user

def execute():
    os.system('clear')
    user = splash()
    player = returning(user.address, user.wallet, user.salt)
    return player ## (account, player)
    
    # if not encrypted_wallet_base64 or not wallet_salt_base64 or not user_address:
    #     noob()
    # else:
    #     returning()

