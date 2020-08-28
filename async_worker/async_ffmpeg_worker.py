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
"""gRPC server that places a ffmpeg task in a Google Cloud Tasks queue.

To deploy this server, an API key must be created for the FFmpeg worker service.
The key and the URL of the FFmpeg worker service are sent to Google Cloud Tasks.

This code requires a service account with the permission to enqueue tasks.
Steps on how to create this service account can be found in the link below:
https://cloud.google.com/tasks/docs/creating-http-target-tasks#sa
"""

from concurrent import futures
import os

import grpc
from google.cloud import tasks_v2
from google.protobuf import json_format

from async_worker.async_ffmpeg_worker_pb2 import AsyncFFmpegRequest
from async_worker.async_ffmpeg_worker_pb2 import AsyncFFmpegResponse
from async_worker import async_ffmpeg_worker_pb2_grpc

PROJECT = os.environ['PROJECT']
QUEUE = os.environ['QUEUE']
LOCATION = os.environ['LOCATION']
HOST = os.environ['SERVICE_IP']
API_KEY = os.environ['FFMPEG_API_KEY']
URL = f'http://{HOST}:8080/FFmpeg/transcode?key={API_KEY}'


class AsyncFFmpegServicer(async_ffmpeg_worker_pb2_grpc.AsyncFFmpegServicer):  # pylint: disable=too-few-public-methods
    """Implements AsyncFFmpeg service"""

    def transcode(self, request: AsyncFFmpegRequest,
                  context) -> AsyncFFmpegResponse:
        """Creates FFmpeg task on Google Cloud Tasks queue.

        The task contains the HTTP target to call and the payload.
        """
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(PROJECT, LOCATION, QUEUE)
        payload = json_format.MessageToJson(request.request,
                                            preserving_proto_field_name=True)
        task = {
            'http_request': {
                'http_method': 'POST',
                'url': URL,
                'body': payload.encode()
            }
        }
        response = client.create_task(parent, task)
        return AsyncFFmpegResponse(task_name=response.name)


if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    async_ffmpeg_worker_pb2_grpc.add_AsyncFFmpegServicer_to_server(
        AsyncFFmpegServicer(), server)
    server.add_insecure_port('[::]:8080')
    server.start()
    server.wait_for_termination()
