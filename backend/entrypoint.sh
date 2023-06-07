#!/bin/bash

set -e

host="db"
port="5432"
cmd="$@"

>&2 echo "!!!!!!!! Check infra_db_1 for available !!!!!!!!"

until nc -z -v ${host} ${port}; do
  >&2 echo "infra_db_1 is unavailable - sleeping"
  sleep 1
done

>&2 echo "infra_db_1 is up - executing command"

exec $cmd