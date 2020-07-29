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

The simplest usage of the CLI is the following:
python3 client.py server-ip ffmpeg-argument ...

The following is a sample command:
python3 client.py 127.0.0.1 -i my-bucket-1/input.mp4 my-bucket-2/output.avi
"""

import argparse
import contextlib
import json
import os
import shlex
import sys

from google.protobuf.json_format import MessageToJson
import grpc

from ffmpeg_worker_pb2 import FFmpegRequest
import ffmpeg_worker_pb2_grpc


def main(args, api_key):
    """Main driver for CLI."""
    channel = grpc.insecure_channel(f'{args.ip}:{args.port}')
    stub = ffmpeg_worker_pb2_grpc.FFmpegStub(channel)
    writer = _get_writer(args.format, args.output_file)
    responses = stub.transcode(
        FFmpegRequest(ffmpeg_arguments=args.ffmpeg_arguments),
        metadata=[('x-api-key', api_key)])
    try:
        for ffmpeg_arguments in _get_ffmpeg_commands(args):
            writer.write_command(ffmpeg_arguments, responses)
    except KeyboardInterrupt:
        responses.cancel()
    writer.close()


def _get_writer(output_format, output_file):
    if output_format == 'json':
        return JsonWriter(output_file)
    return NormalWriter(output_file)


def _get_ffmpeg_commands(args):
    """Obtains all the ffmpeg commands that need to be run."""
    if args.input_file is not None:
        for line in args.input_file:
            yield shlex.split(line)
    else:
        yield args.ffmpeg_arguments


class ResponseWriter:
    """Base class for all writer classes."""

    def __init__(self, output_file):
        self.output_file = output_file

    def write_command(self, command, responses):
        """Writes command and its responses."""

    def close(self):
        """Cleans up writer by closing file."""
        self.output_file.close()


class NormalWriter(ResponseWriter):
    """Writes output in human-readable format."""

    def write_command(self, command, responses):
        """Writes command and its responses in human-readable format."""
        with contextlib.redirect_stdout(self.output_file):
            print(command)
            for response in responses:
                if response.HasField('log_line'):
                    print(response.log_line, end='')
                else:
                    exit_code = _convert_exit_code(
                        response.exit_status.exit_code)
                    if exit_code >= 0:
                        print(f'Exited with code {exit_code}')
                    else:
                        print(f'Killed by signal {-exit_code}')
                    print(response.exit_status.resource_usage)
                    print(f'Real time: {response.exit_status.real_time}')


class JsonWriter(ResponseWriter):
    """Writes output in JSON format.

    The output is not pretty printed.
    The JSON written is an array of objects written by write_command.
    """

    def __init__(self, output_file):
        super().__init__(output_file)
        self._add_comma = False
        print('[', end='', file=self.output_file)

    def write_command(self, command, responses):
        """Writes command and its responses in JSON format.

        Here is rough example of the resulting JSON:
        {
          "command": ["ffmpeg", "-i", "input_file", "output_file"],
          "response": {
            "logs": [...],
            "exit_status": {...}
          }
        }

        The exit_status object follows the structure of the ExitStatus protobuf.
        """
        with contextlib.redirect_stdout(self.output_file):
            if self._add_comma:
                print(',', end='')
            print(f'{{"command":{json.dumps(command)},"response":', end='')
            print('{"logs":[', end='')
            prev_response = next(responses)
            for response in responses:
                print(json.dumps(prev_response.log_line), end='')
                if response.HasField('log_line'):
                    print(',', end='')
                prev_response = response
            print('],', end='')
            print('"exit_status":', end='')
            prev_response.exit_status.exit_code = _convert_exit_code(
                prev_response.exit_status.exit_code)
            print(MessageToJson(prev_response.exit_status,
                                including_default_value_fields=True,
                                preserving_proto_field_name=True),
                  end='')
            print('}}', end='')
            self._add_comma = True

    def close(self):
        """Print a closing bracket to close the array started in __init__"""
        print(']', end='', file=self.output_file)
        super().close()


def _convert_exit_code(exit_code):
    """Converts exit code returned by server to more understandable format"""
    if os.WIFEXITED(exit_code):
        return os.WEXITSTATUS(exit_code)
    return -os.WTERMSIG(exit_code)


def get_api_key():
    api_key = os.getenv('FFMPEG_API_KEY')
    if api_key is None:
        raise KeyError('FFMPEG_API_KEY environment variable not found')
    return api_key


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ip', help='IP address of the FFmpeg service')
    parser.add_argument('--port',
                        '-p',
                        default=80,
                        type=int,
                        help='port of the FFmpeg service')
    parser.add_argument('--input-file',
                        '-i',
                        type=lambda f: open(f) if f != '-' else sys.stdin,
                        help=('file with one ffmpeg command per line;'
                              ' use - for stdin'))
    parser.add_argument('--output-file',
                        '-o',
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='output file for ffmpeg service responses')
    parser.add_argument('--format',
                        '-f',
                        choices=['normal', 'json'],
                        default='normal',
                        help='format for ffmpeg service responses')
    parser.add_argument('ffmpeg_arguments',
                        nargs=argparse.REMAINDER,
                        help='arguments to pass to ffmpeg')
    arguments = parser.parse_args()
    if arguments.input_file is not None and len(arguments.ffmpeg_arguments) > 0:
        parser.error('Cannot use both an input file and an explicit command.')
    main(arguments, get_api_key())
