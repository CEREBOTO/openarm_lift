#!/usr/bin/env bash
# 一键启动升降臂 ROS 2 节点（自动 source 发行版与工作空间）
# 用法:
#   ./run_lift_node.sh
#   ./run_lift_node.sh --ros-args -p serial_port:=/dev/ttyUSB1 -p publish_rate:=2.0
# 工作空间: 优先环境变量 ROS2_WS；否则若本脚本在 .../src/openarm_lift/scripts/ 下则自动推断；
#           否则使用 $HOME/ros2_ws

# 不用 set -u：ROS setup.bash 会访问可能未设置的变量（如 AMENT_TRACE_SETUP_FILES）
set -eo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

WS="${ROS2_WS:-}"
if [[ -z "$WS" ]]; then
  _candidate=$(cd "$SCRIPT_DIR/../../.." && pwd)
  if [[ -f "$_candidate/install/setup.bash" ]]; then
    WS="$_candidate"
  fi
fi
if [[ -z "$WS" ]]; then
  WS="$HOME/ros2_ws"
fi

_ros_setup=""
for dist in humble jazzy iron rolling; do
  if [[ -f "/opt/ros/${dist}/setup.bash" ]]; then
    _ros_setup="/opt/ros/${dist}/setup.bash"
    break
  fi
done

if [[ -z "$_ros_setup" ]]; then
  echo "未找到 /opt/ros/{humble,jazzy,iron,rolling}/setup.bash，请先安装 ROS 2。" >&2
  exit 1
fi
# shellcheck source=/dev/null
source "$_ros_setup"

if [[ ! -f "$WS/install/setup.bash" ]]; then
  echo "未找到 $WS/install/setup.bash" >&2
  echo "请设置正确的 ROS2_WS，并在该工作空间编译: colcon build --packages-select openarm_lift" >&2
  exit 1
fi
# shellcheck source=/dev/null
source "$WS/install/setup.bash"

exec ros2 run openarm_lift lift_node "$@"
