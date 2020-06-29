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
"""Runs ffmpeg with GCS files by mounting GCS buckets with gcsfuse.
"""

import os
import pwd
import subprocess
import sys
import tempfile
from typing import List

import ffmpeg_worker_pb2

UNPRIVILEGED_USER = 'ffmpeg-worker'


def main():
    """Runs ffmpeg with GCS files according to the request passed through stdin."""
    request = ffmpeg_worker_pb2.FFmpegRequest()
    request.ParseFromString(bytes.fromhex(sys.stdin.read()))
    with tempfile.TemporaryDirectory() as mount_point:
        _demote_privilege(UNPRIVILEGED_USER, mount_point)
        try:
            _mount_buckets(request.buckets)
            subprocess.run(['ffmpeg', *request.ffmpeg_arguments],
                           stderr=subprocess.STDOUT,
                           check=True)
        finally:
            _unmount_buckets(request.buckets)


def _mount_buckets(buckets: List[str]) -> None:
    """Mounts GCS buckets in the current directory.

    Args:
        buckets: The names of the buckets to mount.
    """
    for bucket in buckets:
        os.mkdir(bucket)
        subprocess.run(['gcsfuse', bucket, bucket], check=True)


def _unmount_buckets(buckets: List[str]) -> None:
    """Unmounts GCS buckets in the current directory.

    Args:
        buckets: The names of the buckets to unmount.
    """
    for bucket in buckets:
        subprocess.run(['fusermount', '-u', bucket], check=True)


def _demote_privilege(user, mount_point) -> None:
    """Sets the uid to an unprivileged user for security reasons.

    Information about security concerns with gcsfuse can be found below.
    https://github.com/GoogleCloudPlatform/gcsfuse/blob/master/docs/mounting.md#mounting
    https://github.com/GoogleCloudPlatform/gcsfuse/blob/master/docs/mounting.md#access-permissions

    Args:
        user: The unprivileged user that we want to run the process as.
        mount_point: The mount point that gcsfuse will mount buckets in.
    """
    user_entry = pwd.getpwnam(user)
    os.chown(mount_point, user_entry.pw_uid, user_entry.pw_gid)
    os.chdir(mount_point)
    os.setgid(user_entry.pw_gid)
    os.setuid(user_entry.pw_uid)


if __name__ == '__main__':
    main()
