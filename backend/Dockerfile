FROM python:3.7-slim

WORKDIR /app

RUN apt-get update && apt-get install -y netcat

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod +x ./entrypoint.sh ./start.sh

ENTRYPOINT [ "./entrypoint.sh" ]

CMD ["./start.sh"]