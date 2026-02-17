FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Remove stale Yarn apt repository with expired GPG key (NO_PUBKEY 62D54FD4003F6525)
# This prevents docker-in-docker and other features from failing on apt-get update
RUN rm -f /etc/apt/sources.list.d/yarn.list && \
    apt-get update && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
