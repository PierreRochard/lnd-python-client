# LND Python Client

This wraps around the grpc API. I'm currently just using it to learn more about 
Lightning. Feel free to fork, branch, and submit PRs!

# Notes

To update the auto-generated grpc code:

1. `curl -o rpc.proto -s https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/rpc.proto`

2. `python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. rpc.proto`

[More details here](https://github.com/lightningnetwork/lnd/blob/master/docs/grpc/python.md)

