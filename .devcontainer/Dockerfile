FROM lukewiwa/pythons

RUN ln -sf /usr/local/bin/python3.6 /usr/local/bin/python
RUN ln -sf /usr/local/bin/pip3.6 /usr/local/bin/pip

RUN apt update && apt install -y sqlite3

ENV MYPY_CACHE_DIR="/tmp/.mypy_cache"
