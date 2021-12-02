# ###########
# Build Stage
# ###########
FROM alpine:3 AS build

# IMAGE INFO
LABEL maintainer="Alexander Barber <alex@dangerzonegames.com>"

# Paper Options
ARG JAVA_VERSION
ARG PAPER_VERSION
ARG PAPER_BUILD
ARG PAPER_FILENAME
ARG PAPER_SHA256
ARG PAPER_DOWNLOAD_URL=https://papermc.io/api/v2/projects/paper/versions/${PAPER_VERSION}/builds/${PAPER_BUILD}/downloads/${PAPER_FILENAME}
ARG BUILD_USER=build

# Build
RUN apk add openjdk${JAVA_VERSION}-jdk --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing
ENV BUILD_PATH=/opt/minecraft
WORKDIR ${BUILD_PATH}
ADD ${PAPER_DOWNLOAD_URL} paper.jar
RUN sha256sum paper.jar
RUN echo "${PAPER_SHA256} paper.jar" | sha256sum -c -
RUN adduser --disabled-password --shell /bin/bash ${BUILD_USER} && \
    chown ${BUILD_USER} ${BUILD_PATH} -R
USER ${BUILD_USER}
RUN java -jar ${BUILD_PATH}/paper.jar; exit 0
RUN mv ${BUILD_PATH}/cache/patched_${PAPER_VERSION}.jar ${BUILD_PATH}/paper.jar


# #########################
# Runtime Environment Stage
# #########################
FROM alpine:3 AS run

# IMAGE INFO
LABEL maintainer="Alexander Barber <alex@dangerzonegames.com>"

# Config Run Environment
ARG JAVA_VERSION
ENV MINECRAFT_PATH=/opt/minecraft

# Config Directories
ENV SERVER_PATH=${MINECRAFT_PATH}/server
ENV DATA_PATH=${MINECRAFT_PATH}/data
ENV LOGS_PATH=${MINECRAFT_PATH}/logs
ENV CONFIG_PATH=${MINECRAFT_PATH}/config
ENV WORLDS_PATH=${MINECRAFT_PATH}/worlds
ENV PLUGINS_PATH=${MINECRAFT_PATH}/plugins
ENV PROPERTIES_PATH=${CONFIG_PATH}/server.properties

# Config VM
ENV JAVA_HEAP_SIZE_INIT=4G
ENV JAVA_HEAP_SIZE_MAX=4G
ENV JAVA_STACK_SIZE=1M
ENV JAVA_ARGS="-server -Dcom.mojang.eula.agree=true"
ENV SPIGOT_ARGS="--nojline --nogui"
ENV PAPER_ARGS=""

# Health Check
RUN apk add python3 py3-pip
RUN pip3 install --upgrade pip setuptools
RUN pip3 install mcstatus
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s \
    CMD mcstatus localhost:$( cat $PROPERTIES_LOCATION | grep "server-port" | cut -d'=' -f2 ) ping

# Install Paper
WORKDIR ${SERVER_PATH}
COPY --from=build /opt/minecraft/paper.jar ${SERVER_PATH}/

# Setup Environment
ADD docker-entrypoint.sh docker-entrypoint.sh
RUN apk add bash
RUN apk add openjdk${JAVA_VERSION}-jdk --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing
RUN chmod +x docker-entrypoint.sh
RUN addgroup minecraft && \
    adduser --disabled-password --home ${MINECRAFT_PATH} --shell /bin/bash minecraft -G minecraft && \
    mkdir -p ${LOGS_PATH} ${DATA_PATH} ${WORLDS_PATH} ${PLUGINS_PATH} ${CONFIG_PATH} && \
    chown -R minecraft:minecraft ${MINECRAFT_PATH}
USER minecraft

# Symlink to Real Install Paths
# Note: the `/worlds` path is non-standard, but it may be useful for some server backup plugins
RUN ln -s $PLUGINS_PATH                  $SERVER_PATH/plugins           && \
    ln -s $WORLDS_PATH                   $SERVER_PATH/worlds            && \
    ln -s $LOGS_PATH                     $SERVER_PATH/logs              && \
    ln -s $CONFIG_PATH/server-icon.png   $SERVER_PATH/server-icon.png   && \
    ln -s $CONFIG_PATH/server.properties $SERVER_PATH/server.properties && \
    ln -s $CONFIG_PATH/commands.yml      $SERVER_PATH/commands.yml      && \
    ln -s $CONFIG_PATH/bukkit.yml        $SERVER_PATH/bukkit.yml        && \
    ln -s $CONFIG_PATH/spigot.yml        $SERVER_PATH/spigot.yml        && \
    ln -s $CONFIG_PATH/paper.yml         $SERVER_PATH/paper.yml         && \
    ln -s $DATA_PATH/permissions.yml     $SERVER_PATH/permissions.yml   && \
    ln -s $DATA_PATH/help.yml            $SERVER_PATH/help.yml          && \
    ln -s $DATA_PATH/ops.json            $SERVER_PATH/ops.json          && \
    ln -s $DATA_PATH/whitelist.json      $SERVER_PATH/whitelist.json    && \
    ln -s $DATA_PATH/banned-ips.json     $SERVER_PATH/banned-ips.json   && \
    ln -s $DATA_PATH/banned-players.json $SERVER_PATH/banned-players.json

# Volumes
VOLUME "${CONFIG_PATH}"
VOLUME "${WORLDS_PATH}"
VOLUME "${PLUGINS_PATH}"
VOLUME "${DATA_PATH}"
VOLUME "${LOGS_PATH}"

# Open Ports
# ==========
# NOTE: I'm exposing a range here so that you can open 25565 (the usual
# port minecraft uses), 25575 (the usual port that RCON uses), and then an
# additional 20 ports (25580-25599) are available in case you use plugins that
# need to bind ports on the machine, such as for web interfaces or APIs. You
# will probably need to configure your plugins to use one of these instead of
# their default.
EXPOSE 25565
EXPOSE 25575
EXPOSE 25580-25599

# Run Command
ENTRYPOINT [ "./docker-entrypoint.sh" ]
CMD [ "start" ]
