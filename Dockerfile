FROM python:3.8.5-alpine3.11 AS py_venv_builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /greeting

COPY requirements.txt .

RUN python3 -m venv ./venv
RUN source ./venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && deactivate

FROM python:3.8.5-alpine3.11

ARG BUILD_DATE

ENV APP_CONFIG=/greeting/config/config.yml
ENV LOG_CONFIG=/greeting/config/logging.yml

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["bin/run.sh"]

CMD []

LABEL "org.label-schema.name"="jonathanp62/greeting"
LABEL "org.label-schema.description"="A sample program for Docker"
LABEL "org.label-schema.schema-version"="1.0"
LABEL "org.label-schema.vendor"="Penguin Random House, LLC"
LABEL "org.label-schema.vcs-url"="svn://localhost/Docker/Greeting/trunk"
LABEL "org.label-schema.docker.cmd"="docker container run -d --name Greeting jonathanp62/greeting"
LABEL "org.label-schema.version"="0.1.5"
LABEL "org.label-schema.vcs-ref"="12821"
LABEL "org.label-schema.build-date"=$BUILD_DATE

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

USER appuser

WORKDIR /greeting

COPY --from=py_venv_builder /greeting/venv ./venv/
COPY bin bin/
COPY config config/
COPY main.py .
