FROM python:3.10

RUN apt update && apt install -y ffmpeg

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
