#!/bin/bash
set -x

GF_PATHS_DATA=${GF_PATHS_DATA:-"/grafana/data"}
GF_PATHS_PLUGINS=${GF_PATHS_PLUGINS:-"/grafana/plugins"}
GF_PATHS_LOGS=${GF_PATHS_LOGS:-"/grafana/logs"}
#
CONSOLE_OUTPUT=${CONSOLE_OUTPUT:-"no"}
LOG_PATH=${LOG_PATH:-"/grafana/logs/grafana.log"}

mkdir -p $GF_PATHS_DATA $GF_PATHS_PLUGINS $GF_PATHS_LOGS `dirname $LOG_PATH`

function start_grafana() {
    chown -R grafana:grafana "$GF_PATHS_DATA" "$GF_PATHS_LOGS" "/etc/grafana"
    if [ ! -z "${GF_INSTALL_PLUGINS}" ]; then
        OLDIFS=$IFS
        IFS=','
        for plugin in ${GF_INSTALL_PLUGINS}
        do
            IFS=$OLDIFS
            grafana-cli  --pluginsDir "${GF_PATHS_PLUGINS}" plugins install ${plugin}
        done
    fi
    exec gosu grafana /usr/sbin/grafana-server \
        --homepath=/usr/share/grafana \
        --config=/etc/grafana/grafana.ini \
        cfg:default.log.mode="file" \
        cfg:default.log.file.format="text" \
	cfg:default.log.file.log_rotate=true \
        cfg:default.log.file.max_days=7 \
        cfg:default.log.file.daily_rotate=true \
        cfg:default.paths.data="$GF_PATHS_DATA" \
        cfg:default.paths.logs="$GF_PATHS_LOGS" \
        cfg:default.paths.plugins="$GF_PATHS_PLUGINS" \
        cfg:default.auth.ldap.enabled=true \
        cfg:default.auth.ldap.enabled=/etc/grafana/ldap.toml
}

echo "############ Start nscd..."
service nscd start
echo "############ Start cron..."
/usr/sbin/cron
# Start
echo "############ Start Grafana..."
start_grafana
sleep 3

if [ x"$CONSOLE_OUTPUT" = x"yes" ];then
    tail -f /grafana/logs/*.log
fi
