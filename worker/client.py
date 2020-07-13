# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Client CLI for interacting with FFmpeg worker.

The usage of the CLI is the following:
python3 client.py server-ip ffmpeg-argument ...

The following is a sample command:
python3 client.py 127.0.0.1 -i my-bucket-1/input.mp4 my-bucket-2/output.avi
"""

import argparse
import os
import sys

import grpc

from ffmpeg_worker_pb2 import FFmpegRequest
import ffmpeg_worker_pb2_grpc


def main(args, api_key):
    """Main driver for CLI."""
    channel = grpc.insecure_channel(f'{args.ip}:{args.port}')
    stub = ffmpeg_worker_pb2_grpc.FFmpegStub(channel)
    for response in stub.transcode(
            FFmpegRequest(ffmpeg_arguments=args.ffmpeg_arguments), metadata=[('x-api-key', api_key)]):
        if response.HasField('log_line'):
            print(response.log_line, end='')
        else:
            if os.WIFEXITED(response.exit_status.exit_code):
                print(f'Exited with code {os.WEXITSTATUS(response.exit_status.exit_code)}')
            else:
                print(f'Killed by signal {os.WTERMSIG(response.exit_status.exit_code)}')
            print(response.exit_status.resource_usage)



def get_api_key():
    api_key = os.getenv('FFMPEG_API_KEY')
    if api_key is None:
        raise KeyError('FFMPEG_API_KEY environment variable not found')
    return api_key


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ip', help='IP address of the FFmpeg service')
    parser.add_argument('--port', '-p', default=80, type=int, help='port of the FFmpeg service')
    parser.add_argument('ffmpeg_arguments', nargs=argparse.REMAINDER, help='arguments to pass to ffmpeg')
    main(parser.parse_args(), get_api_key())
