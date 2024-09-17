#!/bin/bash
set -x

# Downloaded from https://github.com/prometheus/prometheus/releases
REPOSITORY='https://github.com/prometheus/prometheus/releases/download'

PROMETHEUS_VERSION=2.32.1
ARCHIVE=prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz

# Download the archive file
curl -LO ${REPOSITORY}/v${PROMETHEUS_VERSION}/${ARCHIVE}

# Extract the tarball after it's fully downloaded
tar -xzvf ${ARCHIVE} -C /opt

# Create a symlink to the extracted directory
ln -s /opt/prometheus-${PROMETHEUS_VERSION} /opt/prometheus

# Optionally, remove the tarball to save space
rm -f ${ARCHIVE}
