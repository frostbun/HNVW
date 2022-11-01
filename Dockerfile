FROM python:3.10
RUN apt update && apt install ffmpeg -y
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
