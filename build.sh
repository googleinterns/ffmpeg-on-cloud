#!/bin/sh

# Builds gRPC and protobuf code.
# This should be run when `ffmpeg-on-cloud` is the working directory.

python3 -m grpc_tools.protoc \
    --include_imports \
    --include_source_info \
    --proto_path=. \
    --descriptor_set_out=./api_descriptor.pb \
    --python_out=. \
    --grpc_python_out=. \
    ./worker/ffmpeg_worker.proto \
    ./async_worker/async_ffmpeg_worker.proto
