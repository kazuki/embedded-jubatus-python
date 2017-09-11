#!/bin/bash
set -e

export W=/workdir

export MAKEOPTS=${MAKEOPTS:--j4}
export MSGPACK_VER=${MSGPACK_VER:-0.5.9}
export ONIG_VER=${ONIG_VER:-6.6.1}
export JUBATUS_VER=${JUBATUS_VER:-1.0.5}
export EMBEDDED_VER=${EMBEDDED_VER:-1.0.5}

LATEST_PYTHON=`ls -1 /opt/python/cp3*/bin/python | tail -n 1`
PYBIN_PATTERN=`echo /opt/python/cp{27,34,35,36}-*/bin`  # numpy doesn't support py26/py33

mkdir -p $W

wget -O - https://github.com/msgpack/msgpack-c/releases/download/cpp-${MSGPACK_VER}/msgpack-${MSGPACK_VER}.tar.gz | tar xvz
cd msgpack-${MSGPACK_VER}
./configure --prefix=/usr
make ${MAKEOPTS} && make install && ldconfig

cd $W
wget -O - https://github.com/kkos/oniguruma/releases/download/v${ONIG_VER}/onig-${ONIG_VER}.tar.gz | tar xvz
cd onig-${ONIG_VER}
./configure --prefix=/usr
make ${MAKEOPTS} && make install && ldconfig

cd $W
wget -O - https://github.com/jubatus/jubatus_core/archive/${JUBATUS_VER}.tar.gz | tar xvz
cd jubatus_core-${JUBATUS_VER}
${LATEST_PYTHON} ./waf configure --prefix=/usr
${LATEST_PYTHON} ./waf build
${LATEST_PYTHON} ./waf --checkall
${LATEST_PYTHON} ./waf install
ldconfig

cd $W
wget -O - https://github.com/jubatus/embedded-jubatus-python/archive/${EMBEDDED_VER}.tar.gz | tar xvz
cd embedded-jubatus-python-${EMBEDDED_VER}
for PYBIN in ${PYBIN_PATTERN}; do
    "${PYBIN}/pip" install numpy scipy cython
    "${PYBIN}/pip" wheel . -w wheelhouse/
done
for whl in wheelhouse/embedded_jubatus*.whl; do
    auditwheel repair "$whl" -w wheelhouse/
done
for PYBIN in ${PYBIN_PATTERN}; do
    "${PYBIN}/pip" install embedded_jubatus --no-index -f wheelhouse
    "${PYBIN}/python" -m unittest -v
done
cp wheelhouse/embedded_jubatus*.whl /wheels/
