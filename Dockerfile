FROM grafana/grafana:4.4.0
MAINTAINER Chuck Wu <554574099@qq.com>

ENV TERM xterm-256color
WORKDIR /grafana

COPY ./config/apt/sources.list /etc/apt/sources.list

RUN apt-get update \
    && apt-get install --force-yes -y curl vim net-tools procps logrotate nscd \
    && echo "#####Clean the packages" \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

EXPOSE 3000

COPY ./config/logrotate/grafana /etc/logrotate.d/grafana
COPY ./config/grafana/ldap.toml /etc/grafana/ldap.toml

COPY ./script/run.sh /run.sh

ENTRYPOINT /run.sh
