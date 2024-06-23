FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive
ARG AWS_ACCESS_KEY_ID=""
ARG AWS_SECRET_ACCESS_KEY=""
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
RUN apt-get -y update && \
    apt -y full-upgrade && \
    apt -y install curl && \
    apt -y install python3 && \
    apt -y install python3-pip && \
    apt -y install awscli && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install jupyter --break-system-packages --no-cache-dir && \
    python3 -m pip install tensorflow --break-system-packages --no-cache-dir
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]