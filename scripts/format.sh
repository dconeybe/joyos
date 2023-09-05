#!/bin/bash

readonly pyink_args=(
  pyink
  --line-length 100
  --target-version py311
  --pyink
  --pyink-indentation 2
  scripts/*.py
  "$@"
)

echo "${pyink_args[*]}"
"${pyink_args[@]}"
