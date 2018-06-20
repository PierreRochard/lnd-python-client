# Follow the instructions at https://dev.lightning.community/tutorial/01-lncli/index.html
# to set up the lightning simnet nodes

from lnd_client.lightning_client import LightningClient


class LightningNetwork(object):
    def __init__(self):
        self.alice = LightningClient('localhost:10001',
                                     'localhost:10011',
                                     'alice')

        self.bob = LightningClient('localhost:10002',
                                   'localhost:10012',
                                   'bob')

        self.charlie = LightningClient('localhost:10003',
                                       'localhost:10013',
                                       'charlie')

        self.nodes = [self.alice, self.bob, self.charlie]
        self.setup_p2p()

    def setup_p2p(self):
        self.setup_p2p_connection(self.alice, self.bob)
        self.setup_p2p_connection(self.bob, self.charlie)

    @staticmethod
    def setup_p2p_connection(source_node: LightningClient,
                             destination_node: LightningClient):
        try:
            source_node.connect(destination_node.pubkey,
                                destination_node.listening_uri)
        except Exception as exc:
            if 'already connected to peer' in exc._state.details:
                pass
            else:
                raise

    def setup_channels(self):
        # Close existing channels
        for node in self.nodes:
            channels = node.get_channels().channels
            for channel in channels:
                node.close_channel(channel_point=channel.channel_point)

        # Setup new channels
        self.setup_channel(self.bob, self.alice, 1000000, 0)
        self.setup_channel(self.charlie, self.bob, 800000, 200000)

    @staticmethod
    def setup_channel(source_node: LightningClient,
                      destination_node: LightningClient,
                      local_amount: int,
                      push_amount: int):
        pubkey = destination_node.pubkey
        source_node.open_channel(pubkey=pubkey,
                                 local_amount=local_amount,
                                 push_amount=push_amount)

    @staticmethod
    def send_payment(source_node: LightningClient,
                     destination_node: LightningClient,
                     amount: int):
        invoice = destination_node.create_invoice(amount=amount).payment_request
        source_node.send_payment(encoded_invoice=invoice)

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
    import argparse
    parser = argparse.ArgumentParser(description='Update pull request')
    parser.add_argument('-c',
                        dest='setup_channels',
                        type=bool,
                        default=False
                        )
    parser.add_argument('-s',
                        dest='send_payments',
                        type=bool,
                        default=False
                        )
    args = parser.parse_args()

    network = LightningNetwork()

    if args.setup_channels:
        network.setup_channels()

    if args.send_payments:
        network.send_payment(network.alice, network.bob, 2018)
        network.send_payment(network.alice, network.charlie, 2019)

    network.output_info()
