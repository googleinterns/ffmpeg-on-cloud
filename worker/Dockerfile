FROM python:3

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y ffmpeg

COPY . .
RUN pip install --requirement requirements.txt

ENV FLASK_APP ffmpeg_worker.py
CMD [ "flask", "run", "--port=8080", "--host=0.0.0.0" ]

EXPOSE 8080
