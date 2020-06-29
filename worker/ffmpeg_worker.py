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
"""A server that runs FFmpeg on files in Google Cloud Storage.
"""

from concurrent import futures
import logging
import subprocess
from typing import Iterator

from google.cloud import storage
import grpc

from ffmpeg_worker_pb2 import FFmpegRequest
from ffmpeg_worker_pb2 import FFmpegResponse
import ffmpeg_worker_pb2_grpc


class FFmpegServicer(ffmpeg_worker_pb2_grpc.FFmpegServicer):  # pylint: disable=too-few-public-methods
    """Implements FFmpeg service"""

    def transcode(self, request: FFmpegRequest, context) -> FFmpegResponse:
        """Runs ffmpeg according to the request's specification.

        Args:
            request: The FFmpeg request.
            context: The gRPC context.

        Yields:
            A Log object with a line of ffmpeg's output.
        """
        for stdout_data in run_ffmpeg(request):
            yield FFmpegResponse(log_line=stdout_data)


def run_ffmpeg(request: FFmpegRequest) -> Iterator[str]:
    """Runs ffmpeg according to the request and iterates over the output.

    Args:
        request: The request specifying how to run ffmpeg.

    Yields:
        A line of ffmpeg's output.
    """
    with subprocess.Popen(['python3', 'run_ffmpeg.py'],
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          universal_newlines=True,
                          bufsize=1) as pipe:
        pipe.stdin.write(request.SerializeToString().hex())
        pipe.stdin.close()
        for line in pipe.stdout:
            yield line


def serve():
    """Starts the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ffmpeg_worker_pb2_grpc.add_FFmpegServicer_to_server(FFmpegServicer(),
                                                        server)
    server.add_insecure_port('[::]:8080')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
