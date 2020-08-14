# The buildcontext when building this Docker image should be the root directory of the project (ffmpeg-on-cloud/).

FROM python:3

WORKDIR /usr/src/app

COPY async_worker/requirements.txt .
RUN pip install --requirement requirements.txt

COPY worker worker
COPY async_worker/async_ffmpeg_worker_pb2.py async_worker/async_ffmpeg_worker_pb2_grpc.py ./async_worker/
COPY async_worker/async_ffmpeg_worker.py .

CMD [ "python3", "async_ffmpeg_worker.py" ]

EXPOSE 8080
