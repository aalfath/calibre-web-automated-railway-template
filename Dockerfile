# Calibre-Web Automated for Railway.
# Official image, pinned by release tag and digest. Bump both together (see CHANGELOG.md).
FROM crocodilestick/calibre-web-automated:v4.0.8@sha256:5e00373854247750cc3e4479b492ae09293ff5e06ed10177f226634d97888679

# Install the bundled Calibre CLI tools at build time (upstream does it on every first boot).
RUN /app/calibre/calibre_postinstall >/dev/null 2>&1 && calibredb --version

COPY railway-entrypoint.sh /railway-entrypoint.sh
COPY root/ /
RUN chmod 755 /railway-entrypoint.sh /etc/s6-overlay/s6-rc.d/railway-setup/run

# Stop the container (non-zero exit, so Railway restarts it) if a startup step fails.
ENV S6_BEHAVIOUR_IF_STAGE2_FAILS=2

EXPOSE 8083
ENTRYPOINT ["/railway-entrypoint.sh"]
