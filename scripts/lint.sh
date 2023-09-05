#!/bin/bash

readonly pyflakes_args=(
  pyflakes
  scripts/*.py
  "$@"
)

echo "${pyflakes_args[*]}"
"${pyflakes_args[@]}"
