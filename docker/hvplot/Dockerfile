FROM ubuntu:22.04

LABEL maintainer="massimods@met.no"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get -y dist-upgrade && apt-get install -y apt-utils  build-essential git python3.10-venv python3.10-dev libpython3.10-dev libnetcdf-dev

WORKDIR /app
RUN useradd -ms /bin/bash user
COPY ./app /app
RUN chown -R user:user /app
USER user

ENV VIRTUAL_ENV=/home/user/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -U pip
RUN pip install -r requirements.txt

COPY entrypoint.sh /home/user/venv/bin/entrypoint.sh
# RUN chmod +x /home/user/venv/bin/entrypoint.sh

EXPOSE 7000

ENV ORIGIN="0.0.0.0:7000" PORT="7000" PREFIX="" LOG_LEVEL="debug"

COPY ./app /app
ENTRYPOINT ["./home/user/venv/bin/entrypoint.sh"]