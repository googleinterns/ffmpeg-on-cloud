FROM python:3

WORKDIR /usr/src/app

RUN apt-get update \
    && apt-get install -y ffmpeg

COPY requirements.txt .
RUN pip install --requirement requirements.txt

COPY . .

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
