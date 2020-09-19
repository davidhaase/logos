FROM python:3.7-alpine3.12 AS py_venv_builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /logos

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc musl-dev
RUN python3 -m venv ./venv
RUN source ./venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && deactivate
RUN apk del .build-deps gcc musl-dev

FROM python:3.7-alpine3.12

ARG BUILD_DATE

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["bin/run.sh"]

CMD []

LABEL "org.label-schema.name"="davidhaase/logos"
LABEL "org.label-schema.description"="A sample program for Docker"
LABEL "org.label-schema.schema-version"="1.0"
LABEL "org.label-schema.vcs-url"="https://github.com/davidhaase/logos"
LABEL "org.label-schema.docker.cmd"="docker container run -d -p 80:5000 --name Logos davidhaase/logos"
LABEL "org.label-schema.version"="1.0.1"
LABEL "org.label-schema.vcs-ref"="88d7756"
LABEL "org.label-schema.build-date"=$BUILD_DATE

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

USER appuser

WORKDIR /logos

COPY --from=py_venv_builder /logos/venv ./venv/
COPY bin/run.sh bin/
COPY config config/
COPY logos.py .
