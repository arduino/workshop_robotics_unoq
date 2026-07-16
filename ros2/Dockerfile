FROM ros:jazzy-ros-base

ENV ROS_WS=/ros2_ws
WORKDIR ${ROS_WS}

# Install common tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install the ROS 2 demo nodes (talker / listener, Python)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ros-jazzy-demo-nodes-py && \
    rm -rf /var/lib/apt/lists/*

# Copy the workspace sources and install their dependencies
COPY ros2_ws/src ./src
RUN apt-get update && \
    rosdep update && \
    rosdep install --from-paths src --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

# Build the workspace during the image build
RUN . /opt/ros/jazzy/setup.sh && colcon build --symlink-install

# Source ROS 2 in every interactive shell (e.g. "docker compose exec ros2 bash"),
# since exec sessions do not run the entrypoint
RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc && \
    echo "[ -f ${ROS_WS}/install/setup.bash ] && source ${ROS_WS}/install/setup.bash" >> /root/.bashrc

COPY ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
