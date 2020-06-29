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
python3 client.py gcs-bucket ... -- ffmpeg-argument ...

The following is a sample command:
python3 client.py my-bucket-1 my-bucket-2 -- -i my-bucket-1/input.mp4 my-bucket-2/output.avi
"""

import sys

import grpc

from ffmpeg_worker_pb2 import FFmpegRequest
import ffmpeg_worker_pb2_grpc


def main():
    """Main driver for CLI."""
    channel = grpc.insecure_channel('localhost:8080')
    stub = ffmpeg_worker_pb2_grpc.FFmpegStub(channel)
    delimiter_index = sys.argv.index('--', 1)
    buckets = sys.argv[1:delimiter_index]
    ffmpeg_arguments = sys.argv[delimiter_index + 1:]
    for line in stub.transcode(
            FFmpegRequest(ffmpeg_arguments=ffmpeg_arguments, buckets=buckets)):
        print(line.log_line, end='')


if __name__ == '__main__':
    main()
