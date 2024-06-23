FROM tensorflow/tensorflow
COPY ./nn_service/requirements.txt .
RUN apt-get -y update && \
    apt -y full-upgrade && \
    apt -y install python3-pip && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt --break-system-packages --no-cache-dir
COPY ./nn_service/nn.py .
ENTRYPOINT ["python3", "nn.py"]