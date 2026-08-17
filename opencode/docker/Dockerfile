FROM ubuntu:latest

ENV PATH="/root/.opencode/bin:$PATH"
WORKDIR /root
RUN apt update -y && apt install curl -y \
    && curl -fsSL https://opencode.ai/install | bash \
    && command -v opencode || grep -q 'opencode' || { echo >&2 "opencode installation failed"; exit 1; } \
    && opencode completion > /root/.bash_completion \
    && echo 'source /root/.bash_completion' >> /root/.bashrc

ENTRYPOINT ["/bin/bash","-c"]