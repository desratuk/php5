# PHP 5.6 generic test record and limits

Scope: Ubuntu 20.04 amd64, PHP 5.6.40 revision 105 community rebuild. These are
historical results for the retained build/test code. Source manifests/build
scripts are unchanged by the public documentation cleanup. Detailed application
and deployment records are outside this public repository.

## Build and selected regression suite

21 core CLI/FPM/module packages, including mcrypt, built and installed. PHP module
API 20131226 and matching full CLI/FPM versions were verified. Config/PID tests,
customized-config preservation, direct FPM startup, FastCGI, sessions, multipart
integrity, OOM without user destructors and subsequent-worker recovery passed.

Native artifact retesting completed with **1,186 passes, zero failures, 274
conditional skips and three warnings**, 1,463 tests total. Warnings are existing
expected-failure cases that now pass. The selected basic/language/serialization/
file/session tests ran with `-n`, so extension-dependent cases may skip. This is
not the full PHP/extension suite or complete security exploit coverage.

An initial harness API expectation was corrected using source/package evidence.
A subsequent OOM fixture was changed to expect the security backport's intentional
safe-stderr leading newline; the test body and fatal-error assertions remained.
No additional test was skipped or reclassified to obtain the passing result.

## Isolated upgrade and actual downgrade

Both historical Surý Focal revisions 62 and 63 passed disposable-container
upgrade/downgrade tests. All 21 core packages upgraded; all 154 synthetic config
entries, CLI/FPM modules and five separate extension versions/binaries were
preserved. Extension checks covered igbinary, Imagick, Memcached, MessagePack
and Redis local APIs; they did not test external service connectivity.

Actual package downgrade, config archive restoration and removal of introduced
libzip5 restored the recorded baseline snapshot. FPM verification passed after
recovery. See [inputs, procedure and limits](upgrade56-isolation.md). This is
neither full-machine/data recovery nor validation of every historical revision.

## Limited application smoke testing

One private Symfony-based application received limited public-page and
authenticated read-only smoke checks with patched FPM on Focal amd64. No
application/vendor compatibility code changes were needed. No application files,
credentials, database contents or deployment-specific comparisons are published.
This is minimal compatibility evidence for one application only.

## Untested / use at own risk

- Full PHP/extension regression suite, independent security auditing and
  exhaustive exploit-based proof of CVE coverage.
- Application writes, submissions, uploads, email, external integrations,
  background jobs/queues and full business workflows.
- General custom extension/multi-PHP coexistence compatibility, every historical
  package revision and every possible host configuration.
- Apache/mod_php, CGI, LiteSpeed, phpdbg, embedded PHP and long-running CLI workers.
- Production performance/load, live systemd integration, other OS versions/
  architectures and complete server/data rollback.
- Independent source-signature verification and ongoing security maintenance.

Containers started FPM directly. A passing package test or homepage does not
establish general production readiness or validate someone else's application.
