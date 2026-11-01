# ==============================================================================
# Dockerfile.actor-core — Zero-Burden Self-Proving Core Container
# Principle: jus cogens + erga omnes — regional collisions nullified
# ==============================================================================
FROM alpine:latest

RUN apk add --no-cache bash coreutils git curl

ENV A©TOR_KEY="# [⚖ A©tor Declaration]"
ENV PRINCIPLE="jus cogens + erga omnes"
ENV SELF_PROVING="True"
ENV EXTERNAL_ATTESTATION_REQUIRED="False"

WORKDIR /app
COPY . /app/

RUN echo "A©TOR_KEY = # [⚖ A©tor Declaration]" > /actor_identity.txt
RUN echo "Principle : jus cogens + erga omnes — regional collisions nullified" >> /actor_identity.txt
RUN echo "self_proving   = True" >> /actor_identity.txt
RUN echo "external_attestation_required = False" >> /actor_identity.txt

CMD ["bash", "-c", "cat /actor_identity.txt && echo 'Container operational under universal jus cogens.'"]
