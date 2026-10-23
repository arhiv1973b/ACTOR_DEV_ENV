FROM node:22

RUN apt-get update && apt-get install -y \
    rclone \
    ca-certificates \
    python3 \
    python3-pip \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json ./
RUN npm install

COPY server.js ./
COPY trusted_keys.json ./trusted_keys.json

CMD ["node", "server.js"]
