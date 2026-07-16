#!/bin/bash
set -e

# Source ROS 2 Jazzy
source /opt/ros/jazzy/setup.bash

# Build the workspace on first start (the host volume shadows the build made
# during "docker build", so we (re)build into the mounted folder once). This
# populates build/ install/ log/ on the host so they persist.
if [ ! -f "${ROS_WS}/install/setup.bash" ] && [ -d "${ROS_WS}/src" ]; then
    echo "Workspace not built yet, running colcon build..."
    cd "${ROS_WS}" && colcon build --symlink-install
fi

# Source the workspace overlay if it has been built
if [ -f "${ROS_WS}/install/setup.bash" ]; then
    source "${ROS_WS}/install/setup.bash"
fi

exec "$@"
