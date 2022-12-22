## BUILD STAGE 1

FROM ubuntu:22.04 as stage0

WORKDIR /opt/

ENV PYTHON_VERSION=3.11.1 \
    PYENV_ROOT=/opt/pyenv \
    PATH=/opt/pyenv/shims:/opt/pyenv/bin:$PATH \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC

RUN set -eux; \
    useradd -U -M -u 1001 -s /bin/false -d /opt penpot; \
    apt-get -qq update; \
    apt-get -qqy --no-install-recommends install \
      binutils \
      build-essential \
      ca-certificates \
      curl \
      sudo \
      git \
      libbz2-dev \
      libffi-dev \
      liblzma-dev \
      libpq-dev \
      libreadline-dev \
      libsasl2-dev \
      libsqlite3-dev \
      libssl-dev \
      libxml2-dev \
      libxmlsec1-dev \
      tzdata \
      xz-utils \
      zlib1g-dev \
    ; \
    rm -rf /var/lib/apt/lists/*;\
    chown -R penpot:penpot /opt;

USER penpot:penpot

RUN git clone https://github.com/pyenv/pyenv.git pyenv

RUN set -ex; \
    pyenv install $PYTHON_VERSION; \
    pyenv global $PYTHON_VERSION; \
    pyenv rehash; \
    pip install -qqq wheel;

COPY --chown=penpot:penpot ./penpot_admin     /opt/penpot_admin
COPY --chown=penpot:penpot ./manage.py        /opt/manage.py
COPY --chown=penpot:penpot ./requirements.txt /opt/requirements.txt

RUN set -ex; \
    pip install -qqqr requirements.txt; \
    python manage.py collectstatic -v 0 --no-input;

## BUILD STAGE 2

FROM ubuntu:22.04 as stage1
LABEL maintainer="Andrey Antukh <niwi@niwi.nz>"

WORKDIR /opt/
ENV PYENV_ROOT=/opt/pyenv \
    PATH=/opt/pyenv/shims:/opt/pyenv/bin:$PATH \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC \
    LANG='en_US.UTF-8' \
    LC_ALL='en_US.UTF-8' \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1

COPY --from=stage0 /opt /opt
COPY ./run.sh /run.sh

RUN set -ex; \
    useradd -U -M -u 1001 -s /bin/false -d /opt penpot; \
    apt-get -qq update; \
    apt-get -qqy --no-install-recommends install \
        curl \
        tzdata \
        locales \
        ca-certificates \
        libpq5 \
    ; \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen; \
    locale-gen; \
    rm -rf /var/lib/apt/lists/*;

EXPOSE 6063
USER penpot:penpot

CMD ["/run.sh"]
