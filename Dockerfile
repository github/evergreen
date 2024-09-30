#checkov:skip=CKV_DOCKER_2
#checkov:skip=CKV_DOCKER_3
FROM python:3.12.6-slim@sha256:ad48727987b259854d52241fac3bc633574364867b8e20aec305e6e7f4028b26
LABEL org.opencontainers.image.source https://github.com/github/evergreen

WORKDIR /action/workspace
COPY requirements.txt *.py /action/workspace/

RUN python3 -m pip install --no-cache-dir -r requirements.txt \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends git=1:2.39.5-0+deb12u1 \
    && rm -rf /var/lib/apt/lists/*

CMD ["/action/workspace/evergreen.py"]
ENTRYPOINT ["python3", "-u"]
