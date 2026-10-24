# PHP 5.6 upgrade and rollback isolation test

This test operates only inside disposable Ubuntu 20.04 amd64 Docker containers.
It does not inspect, install on, or restart any live server.

## Package inputs

Pinned historical baseline package revisions:
`5.6.40-62+ubuntu20.04.1+deb.sury.org+1` and
`5.6.40-63+ubuntu20.04.1+deb.sury.org+2`.
Each baseline contains all 21 installed core packages, including mcrypt.
Candidate: `5.6.40-105+tlb1~ubuntu20.04.1`. Use a reviewed, checksummed build
artifact and inspect its test results; do not trust a version string alone.

Original binary files no longer download from Launchpad's build file links.
Archived PPA copies from Naxonet are checked for exact size and SHA256 against
Launchpad's original HTTPS `.changes` records. Independent GPG validation is not
claimed. The baseline is a representative package installation, not a complete
historical server image or a copy of production configuration/data.

The synthetic baseline pins five separate extension packages:

| Package | Version retained |
| --- | --- |
| php5.6-igbinary | 3.2.6+2.0.8-6+ubuntu20.04.1+deb.sury.org+10 |
| php5.6-imagick | 3.7.0-2+ubuntu20.04.1+deb.sury.org+2 |
| php5.6-memcached | 3.2.0+2.2.0-1+ubuntu20.04.1+deb.sury.org+1 |
| php5.6-msgpack | 1:0.5.7-1+ubuntu20.04.1+deb.sury.org+1 |
| php5.6-redis | 5.3.7+4.3.0-1+ubuntu20.04.1+deb.sury.org+2 |

Archived PPA libpcre3 family 8.45 and libzip4 1.7.3 are supplied from the
previously verified PHP 7.2 isolation-test dependency archive. All mounted
package directories have a SHA256SUMS manifest, rechecked inside the container.

## Procedure

`test56-upgrade.sh` uses read-only `/repo`, `/old`, `/extensions`, `/deps` and
`/candidate` mounts, with reports/backups written to `/out`.

1. Install the original core and separate extension packages in fresh Focal.
2. Add synthetic master/pool/INI customizations and INI symlinks; archive the
   config tree and record content hashes, modes, ownership, symlink targets,
   package versions, CLI/FPM modules and separate extension binary hashes.
3. Verify packaged FPM configuration, PID file, FastCGI response, custom INI
   value and basic operations on all five separate extensions.
4. Save APT's upgrade simulation, then upgrade the 21 core packages with
   `--no-remove`, `--force-confold` and `UCF_FORCE_CONFFOLD=1`.
5. Compare preservation snapshots, verify packaged FPM again, and run the
   existing patched-FPM session/upload/OOM/recovery security probes.
6. Simulate and execute an actual downgrade to the exact original `.deb` set
   with `--allow-downgrades`. Remove only packages introduced by the upgrade.
7. Restore the archived config tree, compare the entire package/config/module/
   extension snapshot with the baseline, then verify packaged FPM and separate
   extensions again. This does not reset or replace the container for rollback.

The pinned original input sizes/hashes are in
`tests/php56-upgrade-inputs.json`. Download them with
`python3 tests/download56-upgrade-inputs.py` (host Python 3.9+). The manual
`test56-upgrade.yml` workflow requires an explicitly reviewed candidate build-run ID.

Example (run from this checkout, with the verified inputs staged in `out56`):

```bash
mkdir -p out56/upgrade63
docker run --name php56-upgrade63 --platform linux/amd64 \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out56/baseline63:/old:ro" \
  -v "$PWD/out56/baseline-extensions:/extensions:ro" \
  -v "$PWD/out56/baseline-deps:/deps:ro" \
  -v "$PWD/out56/candidate:/candidate:ro" \
  -v "$PWD/out56/upgrade63:/out" \
  ubuntu:20.04 bash /repo/test56-upgrade.sh
```

Use `baseline62`, `upgrade62` and a distinct container name for revision 62.
Never execute the script directly on a host: it intentionally installs,
downgrades and restores configuration inside its disposable container.

## Limits

No real application/database, production config, Redis/Memcached server
connectivity, other PHP version coexistence, systemd service management,
full-machine snapshot or all possible extensions are covered. Containers
verify FPM directly because systemd is not PID 1. Rolling back deliberately
restores the old vulnerable interpreter; this is a recovery test, not a
recommendation to keep an unpatched version.

## Results

Historical native amd64 testing passed both baseline jobs; generic results follow.

| Original revision | Upgrade | Original config entries preserved | Separate extensions | Actual rollback + FPM |
| --- | --- | --- | --- | --- |
| 62 (+deb.sury.org+1) | 21 core packages to revision 105 | 154/154 | All five unchanged; operations passed | Passed, original revision 62 restored |
| 63 (+deb.sury.org+2) | 21 core packages to revision 105 | 154/154 | All five unchanged; operations passed | Passed, original revision 63 restored |

Both upgrade plans added only Focal `libzip5` and removed nothing; rollback
removed that added library. Full package-version/config/module/extension
snapshots matched the baseline after rollback. Config comparisons include
content hashes, permission modes, ownership and symlink targets. Patched FPM
also passed persistent sessions, multipart upload integrity, CLI/FPM OOM without
user destructors and subsequent-worker recovery. These probes run only on the
patched interpreter, since rollback deliberately restores the vulnerable one.

These are historical generic results, not a claim that a new build or this
fresh source snapshot was retested. Local emulated setup attempts are not counted
as successful results. This does not establish any live application's compatibility.
