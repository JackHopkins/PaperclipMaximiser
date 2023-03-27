FROM factoriotools/factorio:1.1.76

ARG CACHEBUST=4

COPY config /factorio/config

COPY mods factorio/mods

RUN ["chmod", "+x", "/scenario.sh"]