FROM python:3.7-slim-buster

RUN apt-get update && apt-get install -y g++ dumb-init libev-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY run.bjoern.py run.bjoern.py
COPY geocoder_app geocoder_app/

EXPOSE 5000

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python3", "run.bjoern.py"]