#!/bin/bash

set -euo pipefail

exec objdump -b binary -m i386 -D build/boot
