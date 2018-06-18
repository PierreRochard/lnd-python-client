# Follow the instructions at https://dev.lightning.community/tutorial/01-lncli/index.html
# to set up the lightning simnet nodes

from lnd_client.lightning_client import LightningClient


for user, rpc_server in [('alice', 'localhost:10001'),
                         ('bob', 'localhost:10002'),
                         ('charlie', 'localhost:10003')]:
    user_client = LightningClient(rpc_server=rpc_server,
                                  data_path=f'~/go/dev/{user}/data')
    info = user_client.get_info()
    print(info)
    balance = user_client.get_balance()
    print(balance)
    address = user_client.get_new_address()
    print(address)

