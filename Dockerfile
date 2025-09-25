#checkov:skip=CKV_DOCKER_2
#checkov:skip=CKV_DOCKER_3
#trivy:ignore:AVD-DS-0002
FROM python:3.13.7-slim@sha256:58c30f5bfaa718b5803a53393190b9c68bd517c44c6c94c1b6c8c172bcfad040
LABEL org.opencontainers.image.source https://github.com/github/evergreen

WORKDIR /action/workspace
COPY requirements.txt *.py /action/workspace/

RUN python3 -m pip install --no-cache-dir -r requirements.txt \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends git=1:2.47.3-0+deb13u1 \
    && rm -rf /var/lib/apt/lists/*

# Add a simple healthcheck to satisfy container scanners
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python3 -c "import os,sys; sys.exit(0 if os.path.exists('/action/workspace/evergreen.py') else 1)"

CMD ["/action/workspace/evergreen.py"]
ENTRYPOINT ["python3", "-u"]
