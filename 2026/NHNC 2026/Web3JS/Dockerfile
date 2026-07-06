FROM ubuntu:24.04

# Runtime deps: socat to serve over TCP, plus a toolchain (removed after use)
# to build the setuid readflag helper.
RUN apt-get update && \
    apt-get install -y --no-install-recommends socat gcc libc6-dev ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Unprivileged user that runs the untrusted d8 scripts.
RUN useradd -m -u 1337 ctf

# readflag: setuid-root helper that prints the flag.
COPY readflag.c /tmp/readflag.c
RUN gcc -O2 -static -o /readflag /tmp/readflag.c && \
    rm /tmp/readflag.c && \
    apt-get purge -y gcc libc6-dev && apt-get autoremove -y && \
    chown root:root /readflag && chmod 4755 /readflag

# Challenge engine + connection handler.
RUN mkdir -p /opt/chal
COPY d8 snapshot_blob.bin icudtl.dat /opt/chal/
COPY serve.sh /opt/chal/serve.sh
RUN chmod 755 /opt/chal/d8 /opt/chal/serve.sh

# The real flag: readable only by root (forces use of /readflag via RCE).
COPY flag.txt /flag.txt
RUN chown root:root /flag.txt && chmod 0400 /flag.txt

EXPOSE 5000
USER ctf
CMD ["socat", "-T120", "TCP-LISTEN:5000,reuseaddr,fork", "EXEC:/opt/chal/serve.sh,stderr"]
