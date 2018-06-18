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
    def __init__(self, rpc_server: str, data_path: str = None):
        if platform == "linux" or platform == "linux2":
            path = '~/.lnd/'
        elif platform == "darwin":
            path = '~/Library/Application Support/Lnd/'
        else:
            raise Exception(f"What's the {platform} path for the lnd tls cert?")
        self.main_lnd_path = os.path.expanduser(path)

        if data_path is None:
            self.data_path = self.main_lnd_path
        else:
            data_path = os.path.expanduser(data_path)
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

        self.grpc_channel = grpc.secure_channel(rpc_server,
                                                self.credentials)
        self.lnd_client = lnrpc.LightningStub(self.grpc_channel)

    def get_info(self) -> ln.GetInfoResponse:
        return self.lnd_client.GetInfo(ln.GetInfoRequest())

    def get_balance(self) -> ln.WalletBalanceResponse:
        return self.lnd_client.WalletBalance(ln.WalletBalanceRequest())

    def get_new_address(self) -> ln.NewAddressResponse:
        return self.lnd_client.NewAddress(ln.NewAddressRequest())
