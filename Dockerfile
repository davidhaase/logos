# Multi-Layer Docker file for Logos
# Layer 1 - Choose OS, Python and build virtual environment
FROM python:3.7-alpine3.12 AS py_venv_builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP logos.py
WORKDIR /logos
COPY requirements.txt .

# 1a -- this is special code added because of an error with with "typed-ast" python library,
# Error requires a gcc instance that alpine does nto have
RUN apk add --no-cache --virtual .build-deps gcc musl-dev

RUN python3 -m venv ./venv
RUN source ./venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && deactivate

# 1b (now remove the gcc instance that you added in 1a)
RUN apk del .build-deps gcc musl-dev

# Layer 2 - Copy everything into the container
FROM python:3.7-alpine3.12

# Define environment variables
ARG BUILD_DATE
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
EXPOSE 5000
ENTRYPOINT ["bin/docker-run.sh"]
CMD []

# Define Labels (documentation purposes only)LABEL "org.label-schema.name"="davidhaase/logos"
LABEL "org.label-schema.description"="A sample program for Docker"
LABEL "org.label-schema.schema-version"="1.0"
LABEL "org.label-schema.vcs-url"="https://github.com/davidhaase/logos"
LABEL "org.label-schema.docker.cmd"="docker container run -d -p 80:5000 --name Logos davidhaase/logos"
LABEL "org.label-schema.version"="1.0.1"
LABEL "org.label-schema.vcs-ref"="88d7756"
LABEL "org.label-schema.build-date"=$BUILD_DATE

# Avoid using root user, create a new group and user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
WORKDIR /logos

COPY --from=py_venv_builder /logos/venv ./venv/
COPY bin/docker-run.sh bin/
COPY app app
COPY config config/
COPY logos.py .
COPY config.py .
