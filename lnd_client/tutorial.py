# Follow the instructions at https://dev.lightning.community/tutorial/01-lncli/index.html
# to set up the lightning simnet nodes

from lnd_client.lightning_client import LightningClient

alice = LightningClient('localhost:10001', 'localhost:10011', 'alice')
bob = LightningClient('localhost:10002', 'localhost:10012', 'bob')
charlie = LightningClient('localhost:10003', 'localhost:10013', 'charlie')

nodes = [alice, bob, charlie]

for index, user_client in enumerate(nodes):
    info = user_client.get_info()
    print(info)
    balance = user_client.get_balance()
    print(balance)
    address = user_client.get_new_address()
    print(address)

    peers = user_client.get_peers()
    print(peers)

    if index and not peers:
        peer = nodes[index-1]
        user_client.connect(peer.pubkey, peer.listening_uri)
