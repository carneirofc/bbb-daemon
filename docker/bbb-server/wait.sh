#!/usr/bin/env bash

cd /root/wait-for-it/
./wait-for-it.sh -t 0 $REDIS_SERVER_IP:$REDIS_SERVER_PORT
echo "Redis is UP!"
cd /root/bbb-daemon/

if [ ${CHECKOUT_BRANCH+x} ]; then
	git checkout $CHECKOUT_BRANCH
fi

git pull
cd /root/bbb-daemon/server/
./run.sh
