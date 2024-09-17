yum clean all
rm -rf /var/cache/yum /var/log/*
find /etc -name '*.rpmnew' -delete -o -name '*.rpmsave' -delete
