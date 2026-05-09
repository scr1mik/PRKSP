#!/usr/bin/env bash

for i in {1..228}; do
  curl -s http://127.0.0.1:8080/api/instance
  echo
done | sed -n 's/.*"hostname":"\([^"]*\)".*/\1/p' | sort | uniq -c
