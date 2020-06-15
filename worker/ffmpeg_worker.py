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

import os
import subprocess
from typing import Tuple

from flask import Flask
from flask import request
from flask import safe_join
from google.cloud import storage
from google.cloud.exceptions import NotFound

app = Flask(__name__)


@app.errorhandler(NotFound)
def _handle_gcloud_not_found(_):
    return 'Google Cloud storage object not found', 404


@app.route('/ffmpeg', methods=['POST'])
def process_ffmpeg_command():
    """Runs ffmpeg according to the request's specification.

    The POST request supports the following arguments:
        input_file: A GCS input file path
                    Example: bucket_name/path/to/file
        output_file: A GCS output file path
                     Example: bucket_name/path/to/file
    This route changes the video container format by running the following:
        ffmpeg -i {input_file} {output_file}

    Returns:
        A string with the ffmpeg logs.
    """
    remote_input_file = request.form['input_file']
    local_input_file = _localize_filename(remote_input_file)
    download_file(local_input_file, remote_input_file)
    remote_output_file = request.form['output_file']
    local_output_file = _localize_filename(remote_output_file)

    ffmpeg_logs = subprocess.run(
        ["ffmpeg", "-i", local_input_file, local_output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False).stdout
    os.remove(local_input_file)
    upload_file(local_output_file, remote_output_file)
    os.remove(local_output_file)
    return ffmpeg_logs


def download_file(local_filename: str, remote_filename: str) -> None:
    """Downloads the file from Google Cloud Storage

    This function downloads the file to the /tmp directory.

    Args:
        local_filename: the filepath of the downloaded file
        remote_filename: the filename preceded by the Google Cloud Bucket name
                         Example: bucket_name/path/to/file

    Returns:
        None
    """
    client = storage.Client()
    local_filename = _localize_filename(remote_filename)
    os.makedirs(os.path.dirname(local_filename), exist_ok=True)
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
    bucket_name, blob_name = _split_remote_filename(remote_filename)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_filename)


def _split_remote_filename(remote_filename: str) -> Tuple[str, str]:
    """Splits a remote filename into a bucket and a blob name."""
    split_path = os.path.normpath(remote_filename).split('/', 1)
    bucket_name = split_path[0] if len(split_path) >= 1 else ""
    blob_name = split_path[1] if len(split_path) >= 2 else ""
    return bucket_name, blob_name


def _localize_filename(filename: str) -> str:
    """Takes a remote filename and returns its local counterpart.

    Throws an exception if the filename falls out of the directory.
    """
    return safe_join('/tmp/', filename)
