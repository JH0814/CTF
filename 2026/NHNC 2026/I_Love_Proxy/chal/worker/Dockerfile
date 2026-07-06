FROM debian:stable-slim
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        coreutils \
        curl \
        file \
        findutils \
        gawk \
        grep \
        gzip \
        iproute2 \
        iputils-ping \
        jq \
        less \
        lsof \
        netcat-openbsd \
        procps \
        python3-minimal \
        sed \
        strace \
        tar \
        util-linux \
        vim-common \
        wget \
        xxd && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /usr/local/libexec /srv/proxy-work/cache /srv/proxy-work/log /srv/proxy-work/tmp && \
    printf 'edge boot ok\nworker ready\n' > /srv/proxy-work/log/access.log && \
    printf 'sealed\n' > /srv/proxy-work/cache/status.txt
COPY cgid /usr/local/bin/cgid
COPY courier.cgi /usr/local/libexec/courier.cgi
ENV PORT=7000 CGI_BIN=/usr/local/libexec/courier.cgi
WORKDIR /srv/proxy-work
EXPOSE 7000
CMD ["sh", "-c", "if [ -f /run/.proxy-seed ] && [ -r /run/.proxy-seed ]; then cp /run/.proxy-seed /flag.txt; else printf '%s' \"$FLAG\" > /flag.txt; fi && chmod 400 /flag.txt && unset FLAG && exec cgid"]
