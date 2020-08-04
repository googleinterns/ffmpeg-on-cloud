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
import signal
import subprocess
import sys
import tempfile
import threading
import time
from typing import Iterator
from typing import List

from google.protobuf.duration_pb2 import Duration
import grpc

from ffmpeg_worker_pb2 import ExitStatus
from ffmpeg_worker_pb2 import FFmpegRequest
from ffmpeg_worker_pb2 import FFmpegResponse
from ffmpeg_worker_pb2 import ResourceUsage
import ffmpeg_worker_pb2_grpc

MOUNT_POINT = '/buckets/'
_LOGGER = logging.getLogger(__name__)
_ABORT_EVENT = threading.Event()
_GRACE_PERIOD = 20


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
        _LOGGER.info('Starting transcode.')
        cancel_event = threading.Event()

        def handle_cancel():
            _LOGGER.debug('Termination callback called.')
            cancel_event.set()

        context.add_callback(handle_cancel)
        process = Process(['ffmpeg', *request.ffmpeg_arguments])
        if cancel_event.is_set():
            _LOGGER.info('Stopping transcode due to cancellation.')
            return
        if _ABORT_EVENT.is_set():
            _LOGGER.info('Stopping transcode due to SIGTERM.')
            context.abort(grpc.StatusCode.UNAVAILABLE, 'Request was killed with SIGTERM.')
            return
        for stdout_data in process:
            if cancel_event.is_set():
                _LOGGER.info('Killing ffmpeg process due to cancellation.')
                process.terminate()
                return
            if _ABORT_EVENT.is_set():
                _LOGGER.info('Killing ffmpeg process due to SIGTERM.')
                process.terminate()
                break
            yield FFmpegResponse(log_line=stdout_data)
        yield FFmpegResponse(exit_status=ExitStatus(
            exit_code=process.returncode,
            real_time=_time_to_duration(process.real_time),
            resource_usage=ResourceUsage(ru_utime=process.rusage.ru_utime,
                                         ru_stime=process.rusage.ru_stime,
                                         ru_maxrss=process.rusage.ru_maxrss,
                                         ru_ixrss=process.rusage.ru_ixrss,
                                         ru_idrss=process.rusage.ru_idrss,
                                         ru_isrss=process.rusage.ru_isrss,
                                         ru_minflt=process.rusage.ru_minflt,
                                         ru_majflt=process.rusage.ru_majflt,
                                         ru_nswap=process.rusage.ru_nswap,
                                         ru_inblock=process.rusage.ru_inblock,
                                         ru_oublock=process.rusage.ru_oublock,
                                         ru_msgsnd=process.rusage.ru_msgsnd,
                                         ru_msgrcv=process.rusage.ru_msgrcv,
                                         ru_nsignals=process.rusage.ru_nsignals,
                                         ru_nvcsw=process.rusage.ru_nvcsw,
                                         ru_nivcsw=process.rusage.ru_nivcsw)))
        _LOGGER.info('Finished transcode.')


class Process:
    """
    Wrapper class around subprocess.Popen class.
    This class records the resource usage of the terminated process.
    """

    def __init__(self, args):
        self._start_time = None
        self._args = args
        self._subprocess = None
        self.returncode = None
        self.rusage = None
        self.real_time = None

    def __iter__(self):
        self._start_time = time.time()
        self._subprocess = subprocess.Popen(self._args,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            universal_newlines=True,
                                            bufsize=1)
        yield from self._subprocess.stdout
        self.wait()

    def terminate(self):
        """Terminates the process with a SIGTERM signal."""
        if self._subprocess is None:  # process has not been created yet
            return
        self._subprocess.terminate()
        self.wait()

    def wait(self):
        """Waits for the process to finish and collects exit status information."""
        _, self.returncode, self.rusage = os.wait4(self._subprocess.pid, 0)
        self.real_time = time.time() - self._start_time


def serve():
    """Starts the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ffmpeg_worker_pb2_grpc.add_FFmpegServicer_to_server(FFmpegServicer(),
                                                        server)
    server.add_insecure_port('[::]:8080')

    def _sigterm_handler(*_):
        _LOGGER.warning('Recieved SIGTERM. Terminating...')
        _ABORT_EVENT.set()
        server.stop(_GRACE_PERIOD)

    signal.signal(signal.SIGTERM, _sigterm_handler)
    server.start()
    server.wait_for_termination()


def _time_to_duration(seconds: float) -> Duration:
    duration = Duration()
    duration.FromNanoseconds(int(seconds * 10**9))
    return duration


if __name__ == '__main__':
    os.chdir(MOUNT_POINT)
    logging.basicConfig(level=logging.INFO)
    serve()
