#!/bin/bash

set -euo pipefail

exec qemu-system-x86_64 -display curses boot
