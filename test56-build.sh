#!/bin/bash
set -euo pipefail
cd /build/php
phpbin=${PHP_TEST_BIN:-$PWD/cli-build/sapi/cli/php}
[ -x "$phpbin" ]
# The bailout backport prints a leading newline via its safe stderr path.
# Preserve the OOM test body and fatal-error assertion; match that exact format.
patch --batch --forward --fuzz=0 -p1 < /repo/tests/php56-distribution-expectations.patch
# Exercise the built interpreter with PHP's own regression tests, separately
# from Surý's packaging (which disables its built-in test target).
set +e
NO_INTERACTION=1 REPORT_EXIT_STATUS=1 TEST_PHP_EXECUTABLE="$phpbin" \
  "$phpbin" -n run-tests.php -n tests/basic tests/lang ext/standard/tests/serialize \
  ext/standard/tests/file ext/session/tests 2>&1 | tee /out/php56-regression.log
result=${PIPESTATUS[0]}
set -e
find tests ext/session/tests ext/standard/tests/serialize ext/standard/tests/file \
  -name '*.diff' -exec sh -c 'echo "=== $1"; cat "$1"' _ {} \; > /out/php56-test-diffs.txt
printf '%s\n' "$result" > /out/php56-regression-exit.txt
# A nonzero suite result is evidence to investigate, never a successful release.
exit "$result"
