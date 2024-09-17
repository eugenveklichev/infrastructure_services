FROM dzen-external-registry.odkl.ru/oracle9-base:stable
COPY rootfs /
RUN systemctl enable prometheus.service
RUN docker/build
