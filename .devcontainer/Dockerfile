# 安定最短ルート：Ubuntu 24.04 + 系標準Python (3.12)
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04


ENV DEBIAN_FRONTEND=noninteractive PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv python3-pip \
    ffmpeg portaudio19-dev curl git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# python / pip を python3 系へ通す
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    python -m pip install --upgrade pip && \
    pip config set global.only-binary :all: || true

# Node.js (最新安定版)
RUN curl -fsSL https://deb.nodesource.com/setup_current.x | bash - \
 && apt-get update && apt-get install -y nodejs \
 && npm install -g npm@latest corepack \
 && corepack enable || true

# wheels を優先（SciPy/Numpy のビルド地獄を回避）
ENV PIP_ONLY_BINARY=:all:

USER vscode
WORKDIR /workspaces/aituber
