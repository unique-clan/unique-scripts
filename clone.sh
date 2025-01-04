#!/bin/sh

cd /srv/tw
./build_config.py

clone()
{
    echo "====== $3 ======"
    rsync -e "ssh -p $2" --archive --progress --delete \
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
        --include /bin \
        --include /bin/twbuildconf \
        --include /bin/twrestart \
        --include /bin/twstop \
        --include /bin/racerestartwhenempty \
        --include /stdmaps \
        --include /stdmaps/*.cfg.tmpl \
        --include /stdmaps/maps \
        --include /stdmaps/maps/* \
        --include /race \
        --include /race/*.cfg.tmpl \
        --include /race/announcements.txt \
        --include /race/maps \
        --include /race/maps/* \
        --include /race/maps07 \
        --include /race/maps07/* \
        --include /race/restart_when_empty.py \
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
        --include /src/build.py \
        --include /src/mods.json \
	--include /local_config.json.default \
        --exclude '*' \
        /srv/tw/ tw@$1:/srv/tw

    ssh tw@$1 -p $2 << EOF
./build_config.py
EOF
}

clone 54.39.96.248 22 Canada
#clone 104.0.224.113 6620 USA
clone 62.217.186.19 8350 Russia
#clone 38.54.107.120 22 Taiwan
