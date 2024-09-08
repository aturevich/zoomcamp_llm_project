#!/bin/sh
set -e

host="$1"
port="$2"
shift 2
cmd="$@"

until nc -z "$host" "$port"; do
  echo "Waiting for FastAPI ($host:$port) to be ready..."
  sleep 1
done

echo "FastAPI is ready!"
exec $cmd
