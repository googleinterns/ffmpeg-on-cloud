FROM python:3

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y ffmpeg

COPY . .
RUN pip install --requirement requirements.txt

ENV FLASK_APP ffmpeg_worker.py
CMD [ "python3", "ffmpeg_worker.py" ]

EXPOSE 8080
