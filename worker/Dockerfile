# This builder container should contain the ffmpeg binary that will be used
FROM gcr.io/$GCLOUD_PROJECT/ffmpeg AS ffmpeg

FROM python:3

WORKDIR /usr/src/app

COPY --from=ffmpeg /usr/grte/ /usr/grte/
COPY --from=ffmpeg /ffmpeg/ /ffmpeg/
ENV PATH="/ffmpeg:${PATH}"

COPY requirements.txt .
RUN pip install --requirement requirements.txt

COPY ffmpeg_worker_pb2.py ffmpeg_worker_pb2_grpc.py ./worker/
COPY ffmpeg_worker.py .

# The UID below should match the UID used in the gcsfuse DaemonSet.
RUN adduser ffmpeg-worker \
    --system \
    --no-create-home \
    --disabled-password \
    --disabled-login \
    --ingroup daemon \
    --uid 999

USER ffmpeg-worker

CMD [ "python3", "ffmpeg_worker.py" ]

EXPOSE 8080
