#!/usr/bin/env bash 
set -euo pipefail 

: ${BACKUP_DIR:=/backups} 
: ${PGHOST:=localhost} 
: ${PGPORT:=5432} 
: ${PGUSER:=potter} 
: ${PGDATABASE:=pottershouse_prod} 

ts=$(date +%F) 
mkdir -p $BACKUP_DIR 
outfile=$BACKUP_DIR/${PGDATABASE}_${ts}.dump 

pg_dump -h $PGHOST -p $PGPORT -U $PGUSER -Fc -f $outfile $PGDATABASE 

find $BACKUP_DIR -type f -name ${PGDATABASE}_*.dump -mtime +14 -delete 

echo Backup written to $outfile 
