# Experimental PHP 5.6 backport for Ubuntu 20.04 amd64

This repository derives from [Niek/php7](https://github.com/Niek/php7).
It rebuilds **PHP 5.6.40** with Surý's revision 105 security backports for
**Ubuntu 20.04 (Focal), amd64 only**. The PHP 7.2 and PHP 5.6 experiments remain
separate. Upstream attribution and the [MIT license](LICENSE) are retained;
see [source attribution](NOTICE.md).

> [!WARNING]
> **Use entirely at your own risk.** This PHP branch is end-of-life and Ubuntu
> 20.04 is outside standard maintenance. This is an experimental migration aid,
> not a maintained security-support service. Testing is limited; there is no
> guarantee of compatibility, complete security coverage or future updates.
> Keep backups/recovery access and migrate to supported PHP/OS versions.

Candidate: **`5.6.40-105+tlb1~ubuntu20.04.1`**.

## Build scope

Pinned Surý Ubuntu 22.04 **source** is rebuilt against native Focal libraries;
Jammy/Debian binaries are not substituted onto Focal. The retained source patches
include CVE-2026-109618/CVE-2026-109619 bailout fixes. Source sizes/hashes are
checked through `sources56.sha256` and the downloaded `.dsc` manifest;
independent GPG source-signature verification is not claimed.

`build56.sh` retains Surý's package layout, adjusts build dependencies/optional
telemetry headers for Focal and resolves FPM version/PID placeholders.
Separate PECL extensions are not bundled.
Revision 105 also backports multipart limits for CVE-2023-0662; mcrypt and
PHP module API 20131226 are included in the tested package scope.

## Generic validation results

Historical tests of the retained build/test code on Focal amd64:

- Built and installed 21 core CLI/FPM/module packages.
- Config checks, customized-config preservation, direct FPM startup, local
  FastCGI/session/multipart requests, OOM termination without a user destructor
  and subsequent-worker recovery passed.
- Selected native amd64 upstream regression suite: **1,186 passed, zero failed,
  274 conditional skips and three warnings** (1,463 total). The warnings are
  existing expected-failure cases that now pass.
- Disposable upgrades from historical Surý Focal revisions 62 and 63 preserved
  154 synthetic configuration entries, CLI/FPM modules and five separate extension
  versions/binaries. Actual package downgrade/config restoration passed for both.
- One private Symfony-based application received limited read-only smoke
  testing on Focal amd64. This does not establish general application compatibility.

See [test scope and limitations](docs/TESTING.md). The public history/docs
cleanup did not rerun compilation or the regression suite; it does not constitute
new validation of a differently built binary. No application source/data or
operational deployment records are included here.

## Installation status

There is no PHP 5.6 GitHub Release, signed APT repository, automatic updater
or general production installer. CI artifacts are experimental outputs; verify
provenance, hashes and individual results. Deployment needs its own reviewed
simulation, backups and recovery plan. Do not use PHP 7.4 or PHP 7.2 instructions.

## Reproduce in isolation

With Bash and Docker available:

```bash
set -euo pipefail
bash download56.sh
mkdir -p out56
docker run --name php56-focal-build --platform linux/amd64 \
  -v "$PWD:/repo:ro" -v "$PWD/sources56:/sources:ro" -v "$PWD/out56:/out" \
  -e JOBS=4 ubuntu:20.04 \
  bash -c 'bash /repo/build56.sh && bash /repo/test56-install.sh && bash /repo/test56-build.sh' \
  2>&1 | tee out56/build.log
```

Use fresh container/output names for another run. Never run installation/test
scripts directly on a host: they intentionally change disposable containers.
No production config, app data or credentials are required. Inspect individual
result files and exit codes, not just a workflow badge. CI mounts only checked-in
build/test code and source/package inputs; artifacts expire.

The [isolated upgrade/rollback procedure](docs/upgrade56-isolation.md) documents
pinned baseline inputs and the limits of the recovery test. Manual retest workflows
require an explicitly reviewed same-repository artifact run ID.

Source: [Surý PHP 5.6 source pool](https://packages.sury.org/php/pool/main/p/php5.6/).
