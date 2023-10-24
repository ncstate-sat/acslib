FROM satregistry.ehps.ncsu.edu/it/python-image:main as base

WORKDIR /code
ADD requirements /code/requirements

RUN set -ex \
    && BUILD_DEPS=" \
    build-essential \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && pip install -r requirements/base/base.txt \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["ls", "-la"]
