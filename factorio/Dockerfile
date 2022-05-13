FROM factoriotools/factorio:1.1.57

ARG CACHEBUST=4

COPY config /factorio/config

COPY mods factorio/mods

RUN ["chmod", "+x", "/scenario.sh"]