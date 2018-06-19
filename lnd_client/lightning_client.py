import codecs
import os
from sys import platform

import grpc
from grpc._plugin_wrapping import (
    _AuthMetadataPluginCallback,
    _AuthMetadataContext
)

import lnd_client.grpc_generated.rpc_pb2 as ln
import lnd_client.grpc_generated.rpc_pb2_grpc as lnrpc

# Due to updated ECDSA generated tls.cert we need to let gprc know that
# we need to use that cipher suite otherwise there will be a handshake
# error when we communicate with the lnd rpc server.
os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'


class LightningClient(object):
    def __init__(self, rpc_server_uri: str, listening_uri: str, name: str = None):
        self.name = name
        self.listening_uri = listening_uri

        if platform == "linux" or platform == "linux2":
            path = '~/.lnd/'
        elif platform == "darwin":
            path = '~/Library/Application Support/Lnd/'
        else:
            raise Exception(f"What's the {platform} path for the lnd tls cert?")
        self.main_lnd_path = os.path.expanduser(path)

        if name is None:
            self.data_path = self.main_lnd_path
        else:
            data_path = os.path.expanduser(f'~/go/dev/{name}/data')
            if not os.path.exists(data_path):
                raise Exception(f'Invalid path {data_path}')
            self.data_path = data_path

        lnd_tls_cert_path = os.path.join(self.main_lnd_path, 'tls.cert')
        self.lnd_tls_cert = open(lnd_tls_cert_path, 'rb').read()

        cert_credentials = grpc.ssl_channel_credentials(self.lnd_tls_cert)

        admin_macaroon_path = os.path.join(self.data_path, 'admin.macaroon')
        with open(admin_macaroon_path, 'rb') as f:
            macaroon_bytes = f.read()
            self.macaroon = codecs.encode(macaroon_bytes, 'hex')

        def metadata_callback(context: _AuthMetadataPluginCallback,
                              callback: _AuthMetadataContext):
            callback([('macaroon', self.macaroon)], None)

        auth_credentials = grpc.metadata_call_credentials(metadata_callback)

        self.credentials = grpc.composite_channel_credentials(cert_credentials,
                                                              auth_credentials)

        self.grpc_channel = grpc.secure_channel(rpc_server_uri,
                                                self.credentials)
        self.lnd_client = lnrpc.LightningStub(self.grpc_channel)

    def get_info(self) -> ln.GetInfoResponse:
        return self.lnd_client.GetInfo(ln.GetInfoRequest())

    @property
    def pubkey(self):
        return self.get_info().identity_pubkey

    def get_balance(self) -> ln.WalletBalanceResponse:
        return self.lnd_client.WalletBalance(ln.WalletBalanceRequest())

    def get_channels(self) -> ln.ListChannelsResponse:
        return self.lnd_client.ListChannels(ln.ListChannelsRequest())

    def get_new_address(self) -> ln.NewAddressResponse:
        return self.lnd_client.NewAddress(ln.NewAddressRequest())

    def get_peers(self) -> ln.ListPeersResponse:
        return self.lnd_client.ListPeers(ln.ListPeersRequest())

    def connect(self, pubkey: str, listening_uri: str):
        address = ln.LightningAddress(pubkey=pubkey, host=listening_uri)
        request = ln.ConnectPeerRequest(addr=address)
        return self.lnd_client.ConnectPeer(request)

    def open_channel(self, pubkey: str, amount: int):
        request = ln.OpenChannelRequest(node_pubkey=codecs.decode(pubkey, 'hex'),
                                        node_pubkey_string=codecs.encode(pubkey.encode('utf-8'), 'hex'),
                                        local_funding_amount=amount)
        return self.lnd_client.OpenChannel(request)
