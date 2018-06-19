# Follow the instructions at https://dev.lightning.community/tutorial/01-lncli/index.html
# to set up the lightning simnet nodes

from lnd_client.lightning_client import LightningClient


class LightningNetwork(object):
    def __init__(self):
        alice = LightningClient('localhost:10001', 'localhost:10011', 'alice')
        bob = LightningClient('localhost:10002', 'localhost:10012', 'bob')
        charlie = LightningClient('localhost:10003', 'localhost:10013',
                                  'charlie')

        self.nodes = [alice, bob, charlie]

    def setup_p2p(self):
        """
            Create a very simple straight-line network
        """

        for index, user_client in enumerate(self.nodes):
            peers = user_client.get_peers()
            if index and not peers:
                peer = self.nodes[index - 1]
                user_client.connect(peer.pubkey, peer.listening_uri)

    def setup_channels(self):
        for index, user_client in enumerate(self.nodes):
            channels = user_client.get_channels().channels
            if index + 1 < len(self.nodes) and not channels:
                peer = self.nodes[index + 1]
                pubkey = peer.pubkey
                user_client.open_channel(pubkey, 1000000)

    def output_info(self):
        for index, user_client in enumerate(self.nodes):
            print(user_client.name)
            info = user_client.get_info()
            print(info)
            balance = user_client.get_balance()
            print(balance)
            address = user_client.get_new_address()
            print(address)
            peers = user_client.get_peers()
            print(peers)
            channels = user_client.get_channels()
            print(channels)


if __name__ == '__main__':
    network = LightningNetwork()
    network.setup_p2p()
    network.setup_channels()
    network.output_info()
