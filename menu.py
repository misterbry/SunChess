from dotenv import load_dotenv
import os
from time import sleep

def main(w3, account, contract):
    # dev_addr = os.getenv("DEV_ADDRESS")
    dev_key = os.getenv("PRIVATE_KEY")
    dev_account = w3.eth.account.from_key(dev_key)
    
    options = []
    player = contract.functions.getPlayer(account.address).call()
    if player[0] == "":
        user_input = input("Are you ready to join SunChess? (y/n) ")
        while user_input[0] != "y" and user_input[0] != "n":
            user_input = input("Try again. Just type 'y' or 'n' ")
        if user_input[0] == "y":
            os.system('clear')
            print("Transfering gas funds, please wait...")
            transfer_coin(w3, dev_account, account.address, 0.1)
            print("Transfer complete.")
            username = input("What would you like your username to be? ")
            try:
                tx_receipt = contract_tx(w3, account, contract, "requestPlayer", (username, account.address))
                print("Request successful!", tx_receipt[0], "\nYou will be notified upon approval.")
                sleep(2)
                return 0
                
            except Exception as e:
                print("Error while requesting to join:", e)
                sleep(2)
                return 1
        else:
            print("Maybe next time!")
            sleep(2)
            return 2
    else:
        print(f"Welcome back, {player[0]}!")
        sleep(2)
        return player

def contract_tx(w3, account, contract, func_name, args=None):
    pk = account.key.hex()
    # pk = os.getenv("PRIVATE_KEY")
    # dev_addr = os.getenv("DEV_ADDRESS")
    if args:
        gas_estimate = w3.eth.estimate_gas({
            "from": account.address,
            # "from": dev_addr,
            "to": contract.address,
            "data": contract.encode_abi(func_name, args=args)
            }),
        gas_price = w3.eth.gas_price

        tx = contract.functions[func_name](*args).build_transaction({
            "from": account.address,
            # "from": dev_addr,
            "nonce": w3.eth.get_transaction_count(account.address),
            # "nonce": w3.eth.get_transaction_count(dev_addr),
            "gas": gas_estimate[0],
            "gasPrice": gas_price
        })
        signed_tx = w3.eth.account.sign_transaction(tx, pk)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return (tx_hash.hex(), tx_receipt)
    else:
        gas_estimate = w3.eth.estimate_gas({
            "from": account.address,
            # "from": dev_addr,
            "to": contract.address,
            "data": contract.encode_abi(func_name)
            }),
        gas_price = w3.eth.gas_price

        tx = contract.functions[func_name]().build_transaction({
            "from": account.address,
            # "from": dev_addr,
            "nonce": w3.eth.get_transaction_count(account.address),
            # "nonce": w3.eth.get_transaction_count(dev_addr),
            "gas": gas_estimate[0],
            "gasPrice": gas_price
        })
        signed_tx = w3.eth.account.sign_transaction(tx, pk)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return (tx_hash.hex(), tx_receipt)        
    
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
