FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod +x ./start.sh

CMD ["./start.sh"]