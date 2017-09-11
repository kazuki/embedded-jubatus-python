#!/bin/bash
ARGS="--rm -v `pwd`/output:/wheels -v `pwd`/build-wheels.sh:/build-wheels.sh"
if [ -n "$https_proxy" ]; then
    ARGS="$ARGS -e proxy=$proxy -e http_proxy=$http_proxy -e https_proxy=$https_proxy"
fi

mkdir -p output
docker run $ARGS quay.io/pypa/manylinux1_x86_64 /bin/bash /build-wheels.sh
docker run $ARGS quay.io/pypa/manylinux1_i686 /bin/bash /build-wheels.sh
