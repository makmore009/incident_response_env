build:


===== Build Queued at 2026-04-07 15:12:19 / Commit SHA: f7add1a =====

--> FROM ghcr.io/meta-pytorch/openenv-base:latest@sha256:3e478c17bcdee6969218c03d0c1986bdb0db9abd4e763a9180b9014b3dde211a
DONE 0.0s

--> WORKDIR /app
CACHED

--> Restoring cache
DONE 4.8s

--> COPY . /app/env
DONE 0.0s

--> WORKDIR /app/env
DONE 0.0s

--> RUN if ! command -v uv >/dev/null 2>&1; then         curl -LsSf https://astral.sh/uv/install.sh | sh &&         mv /root/.local/bin/uv /usr/local/bin/uv &&         mv /root/.local/bin/uvx /usr/local/bin/uvx;     fi
DONE 0.0s

--> RUN apt-get update && apt-get install -y --no-install-recommends     git     && rm -rf /var/lib/apt/lists/*
Get:1 http://deb.debian.org/debian trixie InRelease [140 kB]
Get:2 http://deb.debian.org/debian trixie-updates InRelease [47.3 kB]
Get:3 http://deb.debian.org/debian-security trixie-security InRelease [43.4 kB]
Get:4 http://deb.debian.org/debian trixie/main amd64 Packages [9671 kB]
Get:5 http://deb.debian.org/debian trixie-updates/main amd64 Packages [5412 B]
Get:6 http://deb.debian.org/debian-security trixie-security/main amd64 Packages [119 kB]
Fetched 10.0 MB in 1s (13.3 MB/s)
Reading package lists...
Reading package lists...
Building dependency tree...
Reading state information...
The following additional packages will be installed:
  git-man libcurl3t64-gnutls liberror-perl libexpat1 libgdbm-compat4t64
  libngtcp2-16 libngtcp2-crypto-gnutls8 libperl5.40 perl perl-modules-5.40
Suggested packages:
  gettext-base git-doc git-email git-gui gitk gitweb git-cvs git-mediawiki
  git-svn sensible-utils perl-doc libterm-readline-gnu-perl
  | libterm-readline-perl-perl make libtap-harness-archive-perl
Recommended packages:
  patch less ssh-client
The following NEW packages will be installed:
  git git-man libcurl3t64-gnutls liberror-perl libexpat1 libgdbm-compat4t64
  libngtcp2-16 libngtcp2-crypto-gnutls8 libperl5.40 perl perl-modules-5.40
0 upgraded, 11 newly installed, 0 to remove and 0 not upgraded.
Need to get 19.4 MB of archives.
After this operation, 106 MB of additional disk space will be used.
Get:1 http://deb.debian.org/debian trixie/main amd64 libexpat1 amd64 2.7.1-2 [108 kB]
Get:2 http://deb.debian.org/debian trixie/main amd64 perl-modules-5.40 all 5.40.1-6 [3019 kB]
Get:3 http://deb.debian.org/debian trixie/main amd64 libgdbm-compat4t64 amd64 1.24-2 [50.3 kB]
Get:4 http://deb.debian.org/debian trixie/main amd64 libperl5.40 amd64 5.40.1-6 [4341 kB]
Get:5 http://deb.debian.org/debian trixie/main amd64 perl amd64 5.40.1-6 [267 kB]
Get:6 http://deb.debian.org/debian trixie/main amd64 libngtcp2-16 amd64 1.11.0-1 [131 kB]
Get:7 http://deb.debian.org/debian trixie/main amd64 libngtcp2-crypto-gnutls8 amd64 1.11.0-1 [29.3 kB]
Get:8 http://deb.debian.org/debian trixie/main amd64 libcurl3t64-gnutls amd64 8.14.1-2+deb13u2 [383 kB]
Get:9 http://deb.debian.org/debian trixie/main amd64 liberror-perl all 0.17030-1 [26.9 kB]
Get:10 http://deb.debian.org/debian trixie/main amd64 git-man all 1:2.47.3-0+deb13u1 [2205 kB]
Get:11 http://deb.debian.org/debian trixie/main amd64 git amd64 1:2.47.3-0+deb13u1 [8862 kB]
debconf: unable to initialize frontend: Dialog
debconf: (TERM is not set, so the dialog frontend is not usable.)
debconf: falling back to frontend: Readline
debconf: unable to initialize frontend: Readline
debconf: (Can't locate Term/ReadLine.pm in @INC (you may need to install the Term::ReadLine module) (@INC entries checked: /etc/perl /usr/local/lib/x86_64-linux-gnu/perl/5.40.1 /usr/local/share/perl/5.40.1 /usr/lib/x86_64-linux-gnu/perl5/5.40 /usr/share/perl5 /usr/lib/x86_64-linux-gnu/perl-base /usr/lib/x86_64-linux-gnu/perl/5.40 /usr/share/perl/5.40 /usr/local/lib/site_perl) at /usr/share/perl5/Debconf/FrontEnd/Readline.pm line 8, `<STDIN>` line 11.)
debconf: falling back to frontend: Teletype
debconf: unable to initialize frontend: Teletype
debconf: (This frontend requires a controlling tty.)
debconf: falling back to frontend: Noninteractive
Fetched 19.4 MB in 0s (100 MB/s)
Selecting previously unselected package libexpat1:amd64.
(Reading database ...
(Reading database ... 5%
(Reading database ... 10%
(Reading database ... 15%
(Reading database ... 20%
(Reading database ... 25%
(Reading database ... 30%
(Reading database ... 35%
(Reading database ... 40%
(Reading database ... 45%
(Reading database ... 50%
(Reading database ... 55%
(Reading database ... 60%
(Reading database ... 65%
(Reading database ... 70%
(Reading database ... 75%
(Reading database ... 80%
(Reading database ... 85%
(Reading database ... 90%
(Reading database ... 95%
(Reading database ... 100%
(Reading database ... 5867 files and directories currently installed.)
Preparing to unpack .../00-libexpat1_2.7.1-2_amd64.deb ...
Unpacking libexpat1:amd64 (2.7.1-2) ...
Selecting previously unselected package perl-modules-5.40.
Preparing to unpack .../01-perl-modules-5.40_5.40.1-6_all.deb ...
Unpacking perl-modules-5.40 (5.40.1-6) ...
Selecting previously unselected package libgdbm-compat4t64:amd64.
Preparing to unpack .../02-libgdbm-compat4t64_1.24-2_amd64.deb ...
Unpacking libgdbm-compat4t64:amd64 (1.24-2) ...
Selecting previously unselected package libperl5.40:amd64.
Preparing to unpack .../03-libperl5.40_5.40.1-6_amd64.deb ...
Unpacking libperl5.40:amd64 (5.40.1-6) ...
Selecting previously unselected package perl.
Preparing to unpack .../04-perl_5.40.1-6_amd64.deb ...
Unpacking perl (5.40.1-6) ...
Selecting previously unselected package libngtcp2-16:amd64.
Preparing to unpack .../05-libngtcp2-16_1.11.0-1_amd64.deb ...
Unpacking libngtcp2-16:amd64 (1.11.0-1) ...
Selecting previously unselected package libngtcp2-crypto-gnutls8:amd64.
Preparing to unpack .../06-libngtcp2-crypto-gnutls8_1.11.0-1_amd64.deb ...
Unpacking libngtcp2-crypto-gnutls8:amd64 (1.11.0-1) ...
Selecting previously unselected package libcurl3t64-gnutls:amd64.
Preparing to unpack .../07-libcurl3t64-gnutls_8.14.1-2+deb13u2_amd64.deb ...
Unpacking libcurl3t64-gnutls:amd64 (8.14.1-2+deb13u2) ...
Selecting previously unselected package liberror-perl.
Preparing to unpack .../08-liberror-perl_0.17030-1_all.deb ...
Unpacking liberror-perl (0.17030-1) ...
Selecting previously unselected package git-man.
Preparing to unpack .../09-git-man_1%3a2.47.3-0+deb13u1_all.deb ...
Unpacking git-man (1:2.47.3-0+deb13u1) ...
Selecting previously unselected package git.
Preparing to unpack .../10-git_1%3a2.47.3-0+deb13u1_amd64.deb ...
Unpacking git (1:2.47.3-0+deb13u1) ...
Setting up libexpat1:amd64 (2.7.1-2) ...
Setting up libgdbm-compat4t64:amd64 (1.24-2) ...
Setting up perl-modules-5.40 (5.40.1-6) ...
Setting up git-man (1:2.47.3-0+deb13u1) ...
Setting up libngtcp2-16:amd64 (1.11.0-1) ...
Setting up libngtcp2-crypto-gnutls8:amd64 (1.11.0-1) ...
Setting up libcurl3t64-gnutls:amd64 (8.14.1-2+deb13u2) ...
Setting up libperl5.40:amd64 (5.40.1-6) ...
Setting up perl (5.40.1-6) ...
Setting up liberror-perl (0.17030-1) ...
Setting up git (1:2.47.3-0+deb13u1) ...
Processing triggers for libc-bin (2.41-12+deb13u2) ...
DONE 4.4s

--> RUN --mount=type=cache,target=/root/.cache/uv     if [ -f uv.lock ]; then         uv sync --frozen --no-install-project --no-editable;     else         uv sync --no-install-project --no-editable;     fi
Using CPython 3.11.15 interpreter at: /usr/local/bin/python3
Creating virtual environment at: .venv
Prepared 108 packages in 1.90s
warning: Failed to hardlink files; falling back to full copy. This may lead to degraded performance.
         If the cache and target directories are on different filesystems, hardlinking may not be supported.
         If this is intentional, set `export UV_LINK_MODE=copy` or use `--link-mode=copy` to suppress this warning.
Installed 108 packages in 295ms

+ aiofile==3.9.0
+ aiofiles==24.1.0
+ annotated-doc==0.0.4
+ annotated-types==0.7.0
+ anyio==4.13.0
+ attrs==26.1.0
+ authlib==1.6.9
+ backports-tarfile==1.2.0
+ beartype==0.22.9
+ brotli==1.2.0
+ cachetools==7.0.5
+ caio==0.9.25
+ certifi==2026.2.25
+ cffi==2.0.0
+ charset-normalizer==3.4.6
+ click==8.3.1
+ cryptography==46.0.6
+ cyclopts==4.10.1
+ distro==1.9.0
+ dnspython==2.8.0
+ docstring-parser==0.17.0
+ docutils==0.22.4
+ email-validator==2.3.0
+ exceptiongroup==1.3.1
+ fastapi==0.135.3
+ fastmcp==3.2.0
+ ffmpy==1.0.0
+ filelock==3.25.2
+ fsspec==2026.3.0
+ gradio==6.10.0
+ gradio-client==2.4.0
+ groovy==0.1.2
+ h11==0.16.0
+ hf-gradio==0.3.0
+ hf-xet==1.4.3
+ httpcore==1.0.9
+ httpx==0.28.1
+ httpx-sse==0.4.3
+ huggingface-hub==1.8.0
+ idna==3.11
+ importlib-metadata==8.7.1
+ jaraco-classes==3.4.0
+ jaraco-context==6.1.2
+ jaraco-functools==4.4.0
+ jeepney==0.9.0
+ jinja2==3.1.6
+ jiter==0.13.0
+ jsonref==1.1.0
+ jsonschema==4.26.0
+ jsonschema-path==0.4.5
+ jsonschema-specifications==2025.9.1
+ keyring==25.7.0
+ markdown-it-py==4.0.0
+ markupsafe==3.0.3
+ mcp==1.26.0
+ mdurl==0.1.2
+ more-itertools==10.8.0
+ numpy==2.4.4
+ openai==2.30.0
+ openapi-pydantic==0.5.1
+ openenv-core==0.2.3
+ opentelemetry-api==1.40.0
+ orjson==3.11.8
+ packaging==26.0
+ pandas==3.0.2
+ pathable==0.5.0
+ pillow==12.2.0
+ platformdirs==4.9.4
+ py-key-value-aio==0.4.4
+ pycparser==3.0
+ pydantic==2.12.5
+ pydantic-core==2.41.5
+ pydantic-settings==2.13.1
+ pydub==0.25.1
+ pygments==2.20.0
+ pyjwt==2.12.1
+ pyperclip==1.11.0
+ python-dateutil==2.9.0.post0
+ python-dotenv==1.2.2
+ python-multipart==0.0.22
+ pytz==2026.1.post1
+ pyyaml==6.0.3
+ referencing==0.37.0
+ requests==2.33.1
+ rich==14.3.3
+ rich-rst==1.3.2
+ rpds-py==0.30.0
+ safehttpx==0.1.7
+ secretstorage==3.5.0
+ semantic-version==2.10.0
+ shellingham==1.5.4
+ six==1.17.0
+ sniffio==1.3.1
+ sse-starlette==3.3.4
+ starlette==0.52.1
+ tomli==2.4.1
+ tomli-w==1.2.0
+ tomlkit==0.13.3
+ tqdm==4.67.3
+ typer==0.24.1
+ typing-extensions==4.15.0
+ typing-inspection==0.4.2
+ uncalled-for==0.2.0
+ urllib3==2.6.3
+ uvicorn==0.42.0
+ watchfiles==1.1.1
+ websockets==16.0
+ zipp==3.23.0
  DONE 2.9s

--> RUN --mount=type=cache,target=/root/.cache/uv     if [ -f uv.lock ]; then         uv sync --frozen --no-editable;     else         uv sync --no-editable;     fi
Prepared 1 package in 1.25s
warning: Failed to hardlink files; falling back to full copy. This may lead to degraded performance.
         If the cache and target directories are on different filesystems, hardlinking may not be supported.
         If this is intentional, set `export UV_LINK_MODE=copy` or use `--link-mode=copy` to suppress this warning.
Installed 1 package in 5ms

+ openenv-incident-env==0.1.0 (from file:///app/env)
  DONE 1.6s

--> COPY --from=builder /app/env/.venv /app/.venv
DONE 1.3s

--> COPY --from=builder /app/env /app/env
DONE 1.4s

--> Pushing image
DONE 6.4s

--> Exporting cache
DONE 13.4s

Container: 

===== Application Startup at 2026-04-07 15:13:18 =====

INFO:     Started server process [7]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     10.16.37.110:19416 - "GET /?logs=container HTTP/1.1" 404 Not Found
INFO:     10.16.11.193:55204 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.16.8.212:52610 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.16.11.193:55204 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.16.46.123:22959 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.16.46.123:47026 - "GET / HTTP/1.1" 404 Not Found
INFO:     10.16.8.212:22695 - "GET / HTTP/1.1" 404 Not Found
