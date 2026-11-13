#!/bin/bash
START=$(date +%s)
set -euo pipefail

REPO=/var/backups/borg
STAGE=/var/backups/jirama-staging
DB=gestion_personnel
STATUS=/var/log/jirama-backup.last
export BORG_PASSCOMMAND="cat /root/.borg-passphrase"

fail(){
	echo "ECHEC $(date '+%F %T') : $1" | tee "$STATUS"
	logger -p user.err -t jirama-backup "ECHEC : $1"
	exit 1
}

trap 'fail "erreur ligne:$LINENO"' ERR

umask 077
rm -rf "$STAGE"; mkdir -p "$STAGE"
trap 'rm -rf "$STAGE"' EXIT

runuser -u postgres -- pg_dump -Fc "$DB" > "$STAGE/$DB.dump"
runuser -u postgres -- pg_dumpall --globals-only > "$STAGE/roles.sql"
pg_restore --list "$STAGE/$DB.dump" > /dev/null

borg create -C zstd --stats \
        "$REPO::{hostname}-{now:%Y-%m-%d_%H:%M:%S}" \
        "$STAGE" \
        /etc/nftables.conf \
        /etc/hostapd \
        /etc/dnsmasq.conf /etc/dnsmasq.d \
        /etc/bind \
        /etc/nginx \
        /etc/postgresql \
        /etc/NetworkManager/conf.d/10-ap0-unmanaged.conf \
        /etc/systemd/system \
        /usr/local/sbin \
        /home/andrianina/Bureau/Jirama_project/app/backend/.env

borg prune --keep-daily 7 --keep-weekly 4 --keep-monthly 3 "$REPO"
borg compact "$REPO"
borg check --repository-only "$REPO"

END=$(date +%s)
echo "OK $(date '+%F %T') duree $((END-START)) s" | tee "$STATUS"
logger -t jirama-backup "OK en $((END-START)) s"
