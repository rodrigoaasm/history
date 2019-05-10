FROM python:3.6-alpine as basis

RUN apk update && apk --no-cache add build-base postgresql-dev libffi-dev git libc6-compat linux-headers bash dumb-init

RUN pip install cython

RUN mkdir -p /usr/src/app/requirements
WORKDIR /usr/src/app

RUN python3 -m venv /usr/src/venv
ENV VIRTUAL_ENV="/usr/src/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ADD . /usr/src/app
RUN ["python", "setup.py", "develop"]

FROM python:3.6-alpine
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--"]

COPY --from=basis /usr/src/venv /usr/src/venv
COPY --from=basis /usr/src/app /usr/src/app

ENV VIRTUAL_ENV="/usr/src/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /usr/src/app

EXPOSE 8000

CMD ["sh", "./docker/falcon-docker-entrypoint.sh", "start"]
