FROM debian:latest

# adding gcsfuse package source with instructions shown below:
# https://github.com/GoogleCloudPlatform/gcsfuse/blob/master/docs/installing.md#ubuntu-and-debian-latest-releases
RUN BUILD_DEPS='lsb-release curl gnupg' \
    && apt-get update \
    && apt-get install -y $BUILD_DEPS \
    && export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s` \
    && echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
    && apt-get update \
    && apt-get install -y gcsfuse \
    && apt-get purge -y $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*
