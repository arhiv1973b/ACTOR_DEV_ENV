FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp

RUN groupadd -g 1000 actor_group && \
    useradd -u 1000 -g actor_group -d /tmp -s /bin/bash actor_user

WORKDIR /app

RUN pip install --no-cache-dir fastmcp mcp

RUN chown -R 1000:1000 /app

USER 1000:1000

CMD ["python", "actor_context_server.py"]
