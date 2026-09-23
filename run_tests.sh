#!/usr/bin/env bash

set -euo pipefail

mkdir -p reports/junit

behave \
  --junit \
  --junit-directory reports/junit \
  --format behave_html_formatter:HTMLFormatter \
  --outfile reports/behave.html \
  "$@"