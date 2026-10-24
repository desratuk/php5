#!/bin/bash
# Disposable Ubuntu 20.04 amd64 only. No host/service or live-site access.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
. /etc/os-release
[ "$ID:$VERSION_ID:$(dpkg --print-architecture)" = ubuntu:20.04:amd64 ]
printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d
chmod +x /usr/sbin/policy-rc.d
apt-get update
apt-get install -y --no-install-recommends python3 ca-certificates
for path in /old /extensions /deps /candidate; do (cd "$path" && sha256sum -c SHA256SUMS); done
apt-get install -y --no-remove /deps/*.deb /old/*.deb /extensions/*.deb
mkdir -p /run/php /out
printf '\n; isolated preservation probe\n' >> /etc/php/5.6/fpm/php-fpm.conf
printf '\n; isolated pool customization\n' >> /etc/php/5.6/fpm/pool.d/www.conf
printf 'memory_limit=192M\ndate.timezone=Europe/London\n' > /etc/php/5.6/mods-available/upgrade-probe.ini
chmod 640 /etc/php/5.6/mods-available/upgrade-probe.ini
for sapi in cli fpm; do
 ln -s /etc/php/5.6/mods-available/upgrade-probe.ini /etc/php/5.6/$sapi/conf.d/99-upgrade-probe.ini
done
# Preserve bytes, modes, ownership and symlinks before package mutation.
tar -cpf /out/original-configs.tar -C / etc/php/5.6
python3 /repo/tests/upgrade56.py snapshot before
python3 /repo/tests/upgrade56.py fpm before
new=()
for file in /old/*.deb; do
 package=$(dpkg-deb -f "$file" Package)
 match=(/candidate/"${package}"_*.deb)
 [ "${#match[@]}" = 1 ] && [ -f "${match[0]}" ]
 new+=("${match[0]}")
done
apt-get -s install "${new[@]}" > /out/upgrade-simulation.txt
UCF_FORCE_CONFFOLD=1 apt-get install -y --no-remove -o Dpkg::Options::=--force-confold "${new[@]}"
python3 /repo/tests/upgrade56.py snapshot upgraded
python3 /repo/tests/upgrade56.py compare upgraded
python3 /repo/tests/upgrade56.py fpm upgraded
python3 /repo/tests/fpm56.py | tee /out/patched-fpm-security.json
# Real downgrade using the exact original packages, not a container reset.
apt-get -s --allow-downgrades install /old/*.deb > /out/rollback-simulation.txt
UCF_FORCE_CONFFOLD=1 apt-get install -y --allow-downgrades --no-remove -o Dpkg::Options::=--force-confold /old/*.deb
python3 - <<'PY' > /out/added-packages.txt
import json,subprocess
from pathlib import Path
before=json.loads(Path('/out/before.json').read_text())['packages']
after=dict(l.split('\t') for l in subprocess.check_output(['dpkg-query','-W','-f=${binary:Package}\t${Version}\n']).decode().splitlines())
for name in sorted(set(after)-set(before)):print(name)
PY
mapfile -t added < /out/added-packages.txt
if [ "${#added[@]}" -gt 0 ]; then apt-get purge -y "${added[@]}"; fi
# Restore the archived config tree in this disposable container only.
rm -rf /etc/php/5.6
tar -xpf /out/original-configs.tar -C /
python3 /repo/tests/upgrade56.py snapshot rollback
python3 /repo/tests/upgrade56.py compare rollback
python3 /repo/tests/upgrade56.py fpm rollback
printf 'Upgrade, config/extension preservation, packaged FPM, security probes and exact rollback passed.\n' > /out/result.txt
