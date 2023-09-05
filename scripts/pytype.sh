#!/bin/bash

readonly pytype_args=(
  pytype
  scripts/*.py
  "$@"
)

echo "${pytype_args[*]}"
"${pytype_args[@]}"
