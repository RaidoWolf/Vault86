#!/bin/bash
set -e

if [[ "$1" = 'start' ]]; then
	java -jar $JAVA_ARGS \
		-Xms$JAVA_HEAP_SIZE_INIT \
		-Xmx$JAVA_HEAP_SIZE_MAX \
		-Xss$JAVA_STACK_SIZE \
		$SERVER_PATH/paper.jar \
		$SPIGOT_ARGS \
		--bukkit-settings $CONFIG_PATH/bukkit.yml \
		--plugins $PLUGINS_PATH \
		--world-dir $WORLDS_PATH \
		--spigot-settings $CONFIG_PATH/spigot.yml \
		--commands-settings $CONFIG_PATH/commands.yml \
		--config $PROPERTIES_PATH \
		--paper-settings $CONFIG_PATH/paper.yml \
		$PAPER_ARGS
fi

exec "$@"
