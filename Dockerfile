#checkov:skip=CKV_DOCKER_2
#checkov:skip=CKV_DOCKER_3
FROM python:3.13.1-slim@sha256:23a81be7b258c8f516f7a60e80943cace4350deb8204cf107c7993e343610d47
LABEL org.opencontainers.image.source https://github.com/github/evergreen

WORKDIR /action/workspace
COPY requirements.txt *.py /action/workspace/

RUN python3 -m pip install --no-cache-dir -r requirements.txt \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends git=1:2.39.5-0+deb12u1 \
    && rm -rf /var/lib/apt/lists/*

CMD ["/action/workspace/evergreen.py"]
ENTRYPOINT ["python3", "-u"]
