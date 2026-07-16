# ROS 2 Jazzy on Arduino UNO Q

A minimal Docker setup to run **ROS 2 Jazzy** on the Arduino UNO Q (arm64 Debian).
The workspace is compiled during the image build, and your package sources live on
the host so they persist and stay editable.

## Contents

| File | Purpose |
|------|---------|
| `Dockerfile` | Builds a `ros:jazzy-ros-base` image and compiles the workspace with `colcon`. |
| `docker-compose.yml` | Runs the container with host networking and a persistent source mount. |
| `ros_entrypoint.sh` | Sources ROS 2 and the workspace overlay on every container start. |
| `ros2_ws/src/` | Put your ROS 2 packages here. |

## Getting the files onto the board

This `ros2` folder from the repository must be copied onto the Arduino UNO Q
before you can build anything — the whole Docker setup runs from it. From your
computer, with the board connected over USB, use `adb push`:

```bash
# adb push <local-path-to>/ros2 <destination-on-board>
adb push -a ./ros2 /home/arduino
```

This creates `/home/arduino/ros2` on the board. All the steps below are run
from inside that folder on the UNO Q.

## Requirement: Changing Docker's default data folder

On the Arduino UNO Q the root partition is small, while `/home` (or another
data partition) has much more space. Docker stores all images, containers and
volumes under `/var/lib/docker` by default, so building a ROS 2 image there can
quickly fill the root partition. Point Docker's data folder to a larger
partition **before building any image**.

> Do this on a fresh Docker install, before you have created any image or
> container. Starting Docker fresh in the new location avoids migrating the old
> data — copying `/var/lib/docker` with `cp` corrupts overlay2's internal
> symlinks and breaks the build.

1. Stop Docker:

   ```bash
   sudo systemctl stop docker
   ```

2. Create the new (empty) data folder, e.g. under `/home/arduino`:

   ```bash
   sudo mkdir -p /home/arduino/docker-data
   ```

3. Tell Docker to use it by editing (or creating) `/etc/docker/daemon.json`:

   ```json
   {
     "data-root": "/home/arduino/docker-data"
   }
   ```

4. Start Docker again — it initializes fresh in the new location:

   ```bash
   sudo systemctl start docker
   ```

5. Verify the new location is in use:

   ```bash
   docker info | grep "Docker Root Dir"
   # -> Docker Root Dir: /home/arduino/docker-data
   ```

You can reclaim the old space with `sudo rm -rf /var/lib/docker`.

## Quick start

Run all these commands from **inside the `ros2` folder** on the board (e.g.
`cd /home/arduino/ros2`) — `docker compose` reads the `docker-compose.yml` and
`Dockerfile` from the current directory.

```bash
# 1. Build the image (installs all dependencies and validates the build)
docker compose build

# 2. Start the container in the background. On the FIRST start the entrypoint
#    runs "colcon build" into the mounted workspace, so build/ install/ log/
#    appear in ./ros2_ws on the board. Watch it finish with: docker compose logs -f
docker compose up -d

# 3. Open an interactive shell inside it (ROS 2 + workspace already sourced)
docker compose exec ros2 bash
```

> **`build/`, `install/`, `log/` on the host appear only after `docker compose up`,
> not after `docker compose build`.** The image build compiles inside the image
> (those layers are shadowed by the host mount at runtime); the host folders are
> produced by the first-start `colcon build`. If you changed the compose file,
> run `docker compose down` first so the container is recreated with the new mount.

Then, **inside the container shell**, you can use ROS 2 directly:

```bash
ros2 topic list
ros2 run <your_package> <your_node>
```

> ROS 2 is sourced by the interactive shell's `.bashrc`. Always open a shell with
> `docker compose exec ros2 bash` first — running `docker compose exec ros2 ros2 ...`
> directly will fail with `executable file not found`, because that form does not
> source the environment.

## Testing with the demo nodes (talker / listener)

The image ships with the ROS 2 [`demo_nodes_py`](https://github.com/ros2/demos/tree/jazzy/demo_nodes_py)
package, which provides the classic **talker** and **listener** example nodes.
Use them to verify your setup works end to end.

1. Start the container and open an interactive shell for the **talker**:

   ```bash
   # on the board
   docker compose up -d
   docker compose exec ros2 bash
   ```

   Then, **inside the container shell**, run the talker:

   ```bash
   ros2 run demo_nodes_py talker
   ```

   You should see it publishing messages:

   ```
   [INFO] [talker]: Publishing: 'Hello World: 1'
   [INFO] [talker]: Publishing: 'Hello World: 2'
   ```

2. In a **second terminal**, open another interactive shell:

   ```bash
   # on the board
   docker compose exec ros2 bash
   ```

   Then, **inside the container shell**, run the listener:

   ```bash
   ros2 run demo_nodes_py listener
   ```

   It receives the messages published by the talker:

   ```
   [INFO] [listener]: I heard: [Hello World: 1]
   [INFO] [listener]: I heard: [Hello World: 2]
   ```

Press `Ctrl+C` in each terminal to stop the nodes.

## Adding your own packages

1. Create or clone packages under `ros2_ws/src/` on the host:

   ```bash
   cd ros2_ws/src
   ros2 pkg create --build-type ament_python my_package
   ```

2. Rebuild the image so dependencies are installed and everything is compiled:

   ```bash
   docker compose up -d --build
   ```

That's it — the entrypoint sources the freshly built workspace automatically.

## Rebuilding without a full image rebuild

While iterating on code, you can rebuild inside the running container instead of
rebuilding the image each time. Open an interactive shell:

```bash
# on the board
docker compose exec ros2 bash
```

Then, **inside the container shell**:

```bash
colcon build --symlink-install
source install/setup.bash
```

## Accessing UNO Q hardware

To reach the board's serial peripherals from the container, edit `docker-compose.yml`
and uncomment the two lines:

```yaml
    volumes:
      - ./ros2_ws/src:/ros2_ws/src
      - /dev:/dev            # <-- uncomment
    privileged: true          # <-- uncomment
```

Then restart:

```bash
docker compose up -d
```



## How persistence works

- The **whole `ros2_ws` folder** is bind-mounted from the host, so it is identical
  inside and outside the container. Your sources **and** the generated
  `build/`, `install/`, `log/` folders live on the board and survive container
  removal and rebuilds.
- During `docker build` the workspace is compiled (which installs all dependencies
  into the image), but because the host mount shadows that build at runtime, the
  entrypoint runs `colcon build` once on the **first** container start to populate
  `build/`/`install/`/`log/` on the host. Later starts detect `install/` and skip
  the build.

## Useful commands

```bash
docker compose ps            # container status
docker compose logs -f       # follow logs
docker compose down          # stop and remove the container
docker compose up -d --build # rebuild image and restart
```

## Configuration

- **`ROS_DOMAIN_ID`** — set in `docker-compose.yml` (default `0`). Change it to isolate
  your ROS 2 network from other machines on the same LAN.
- **Networking** — the container uses `network_mode: host` and `ipc: host` so DDS
  discovery works with other ROS 2 nodes on your network out of the box.
