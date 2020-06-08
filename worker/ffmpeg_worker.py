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

import subprocess

from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/ffmpeg', methods=['POST'])
def process_ffmpeg_command():
    """Runs ffmpeg according to the request's specification.

    The POST request supports the following arguments:
        input_file: the input file in the Google Cloud Bucket specified
        output_file: the output file that should be stored in the Google Cloud Bucket

    Args:

    Returns:
        A string with the ffmpeg logs.
    """
    input_file = request.form['input_file']
    output_file = request.form['output_file']
    return subprocess.run(["ffmpeg", "-i", input_file, output_file],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT).stdout
