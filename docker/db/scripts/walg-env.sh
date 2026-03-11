#!/bin/sh
set -eu

escape_single_quotes() {
  printf "%s" "$1" | sed "s/'/'\\''/g"
}

SYSTEMCONFIG_EXISTS=$(psql -tA -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT to_regclass('public.core_systemconfig') IS NOT NULL;" 2>/dev/null || echo "f")
if [ "$SYSTEMCONFIG_EXISTS" != "t" ]; then
  exit 1
fi

VALUES=$(psql -tA -F '|' -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
SELECT
  backup_enabled,
  backup_s3_endpoint,
  backup_s3_bucket,
  backup_s3_path_prefix,
  backup_access_key_id,
  backup_secret_access_key,
  backup_region,
  backup_force_path_style,
  backup_delta_max_steps,
  backup_retention_full_count
FROM core_systemconfig
WHERE id = 1;
" 2>/dev/null || true)

if [ -z "$VALUES" ]; then
  exit 1
fi

backup_enabled=$(printf "%s" "$VALUES" | cut -d'|' -f1)
endpoint=$(printf "%s" "$VALUES" | cut -d'|' -f2)
bucket=$(printf "%s" "$VALUES" | cut -d'|' -f3)
prefix=$(printf "%s" "$VALUES" | cut -d'|' -f4)
access_key=$(printf "%s" "$VALUES" | cut -d'|' -f5)
secret_key=$(printf "%s" "$VALUES" | cut -d'|' -f6)
region=$(printf "%s" "$VALUES" | cut -d'|' -f7)
force_path_style=$(printf "%s" "$VALUES" | cut -d'|' -f8)
delta_steps=$(printf "%s" "$VALUES" | cut -d'|' -f9)
retain_full=$(printf "%s" "$VALUES" | cut -d'|' -f10)

if [ "$backup_enabled" != "t" ]; then
  exit 2
fi

if [ -z "$endpoint" ] || [ -z "$bucket" ] || [ -z "$access_key" ] || [ -z "$secret_key" ]; then
  exit 3
fi

if [ -z "$prefix" ]; then
  prefix="postgresql"
fi
if [ -z "$region" ]; then
  region="eu-central"
fi
if [ -z "$delta_steps" ]; then
  delta_steps="6"
fi
if [ -z "$retain_full" ]; then
  retain_full="14"
fi

clean_endpoint=$(printf "%s" "$endpoint" | sed 's:/*$::')

echo "export AWS_ACCESS_KEY_ID='$(escape_single_quotes "$access_key")'"
echo "export AWS_SECRET_ACCESS_KEY='$(escape_single_quotes "$secret_key")'"
echo "export AWS_REGION='$(escape_single_quotes "$region")'"
echo "export AWS_ENDPOINT='$(escape_single_quotes "$clean_endpoint")'"
echo "export AWS_S3_FORCE_PATH_STYLE='$( [ "$force_path_style" = "t" ] && echo true || echo false )'"
echo "export WALG_S3_PREFIX='s3://$(escape_single_quotes "$bucket")/$(escape_single_quotes "$prefix")'"
echo "export WALG_DELTA_MAX_STEPS='$(escape_single_quotes "$delta_steps")'"
echo "export WALG_DELTA_ORIGIN='LATEST'"
echo "export WALG_RETENTION_FULL='$(escape_single_quotes "$retain_full")'"