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
import os
import pathlib
import subprocess
import tempfile
from typing import Iterator
from typing import List

from google.cloud import storage
import grpc

from ffmpeg_worker_pb2 import Request, Log
import ffmpeg_worker_pb2_grpc


class FFmpegServicer(ffmpeg_worker_pb2_grpc.FFmpegServicer):
    """Implements FFmpeg service"""

    def transcode(self, request: Request, context) -> Log:
        """Runs ffmpeg according to the request's specification.

        This changes the video container format by running the following:
            ffmpeg -i {request.input_filename} {request.output_filename}

        Args:
            request: The FFmpeg request.
            context: The gRPC context.

        Returns:
            A string with the ffmpeg logs.
        """
        remote_input_file = request.input_filename
        input_format = pathlib.PurePath(remote_input_file).suffix
        remote_output_file = request.output_filename
        output_format = pathlib.PurePath(remote_output_file).suffix
        with tempfile.NamedTemporaryFile(suffix=input_format) as input_file:
            with tempfile.NamedTemporaryFile(
                    suffix=output_format) as output_file:
                download_file(remote_input_file, input_file.name)
                for stdout_data in run_process(
                    ['ffmpeg', '-i', input_file.name, '-y', output_file.name]):
                    yield Log(text=stdout_data)
                upload_file(output_file.name, remote_output_file)


def run_process(command: List[str]) -> Iterator[str]:
    """Runs the process specified and iterates over the output.

    Args:
        command: The command to run
                 Example: ['command', 'argument-1', 'argument-2']

    Yields:
        A line of the command's output.
    """
    with subprocess.Popen(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          universal_newlines=True,
                          bufsize=1) as pipe:
        for line in pipe.stdout:
            yield line


def download_file(remote_filename: str, local_filename: str) -> None:
    """Downloads the file from Google Cloud Storage

    This function downloads the file to the /tmp directory.

    Args:
        local_filename: The filepath of the downloaded file
        remote_filename: A GCS output file path
                         Example: bucket_name/path/to/file

    Returns:
        None
    """
    client = storage.Client()
    with open(local_filename, 'wb') as downloaded_file:
        client.download_blob_to_file('gs://' + remote_filename, downloaded_file)


def upload_file(local_filename: str, remote_filename: str) -> None:
    """Uploads the file from Google Cloud Storage.

    This function uploads the file to the Google Cloud Bucket specified.

    Args:
        local_filename: The filepath of the local file to upload
        remote_filename: A GCS output file path
                         Example: bucket_name/path/to/file

    Returns:
        None
    """
    client = storage.Client()
    bucket_name, blob_name = os.path.normpath(remote_filename).split('/', 1)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_filename)


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
