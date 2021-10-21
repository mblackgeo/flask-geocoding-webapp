FROM python:3.7-slim-buster

RUN apt-get update && apt-get install -y g++ libev-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY config.py config.py
COPY run.bjoern.py run.bjoern.py
COPY webmap webmap/

ENTRYPOINT ["python3", "run.bjoern.py"]