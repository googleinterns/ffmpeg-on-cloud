#!/bin/sh

# Builds gRPC and protobuf code.
# This should be run when `ffmpeg-on-cloud/worker` is the working directory.

python3 -m grpc_tools.protoc \
    --include_imports \
    --include_source_info \
    --proto_path=./protos \
    --descriptor_set_out=api_descriptor.pb \
    --python_out=. \
    --grpc_python_out=. \
    ./protos/ffmpeg_worker.proto
