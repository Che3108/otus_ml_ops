FROM ubuntu:20.04
COPY ./tg_bot/requirements.txt .
RUN apt-get -y update && \
    apt -y full-upgrade && \
    apt -y install python3 && \
    apt -y install python3-pip && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt --break-system-packages --no-cache-dir
COPY ./tg_bot/tg_bot.py .
ENTRYPOINT ["python3", "tg_bot.py"]
