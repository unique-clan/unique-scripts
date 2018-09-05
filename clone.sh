#!/bin/sh

cd /srv/tw
./build_config.py

clone()
{
    rsync --archive --compress --progress --delete \
        --include /tw.py \
        --include /build_config.py \
        --include /restart.py \
        --include /run_tw.py \
        --include /stop.py \
        --include /*.cfg.tmpl \
        --include /storage.cfg \
        --include /servers.json \
        --include /passwords.json \
        --include /setup-iptables.sh \
        --include /systemd \
        --include /systemd/user \
        --include /systemd/user/tw.service \
        --include /.profile \
        --include /bin_ \
        --include /bin_/* \
        --include /stdmaps \
        --include /stdmaps/*.cfg.tmpl \
        --include /stdmaps/maps \
        --include /stdmaps/maps/* \
        --include /race \
        --include /race/*.cfg.tmpl \
        --include /race/announcements.txt \
        --include /race/maps \
        --include /race/maps/* \
        --include /flycfg \
        --include /flycfg/*.cfg.tmpl \
        --include /flycfg/maps \
        --include /flycfg/maps/* \
        --include /teesmashcfg \
        --include /teesmashcfg/*.cfg.tmpl \
        --include /teesmashcfg/maps \
        --include /teesmashcfg/maps/* \
        --include /footcfg \
        --include /footcfg/*.cfg.tmpl \
        --include /footcfg/maps \
        --include /footcfg/maps/* \
        --include /src \
        --include /src/mods.json \
        --include /src/unique-race \
        --include /src/unique-race/build \
        --include /src/unique-race/build/DDNet-Server \
        --include /src/fly \
        --include /src/fly/teeworlds_srv \
        --include /src/teesmash \
        --include /src/teesmash/teeworlds_srv \
        --include /src/football \
        --include /src/football/teeworlds_srv \
        --exclude '*' \
        /srv/tw/ tw@$1:/srv/tw

    ssh tw@$1 << EOF
./build_config.py
EOF
}

clone 54.39.23.96
