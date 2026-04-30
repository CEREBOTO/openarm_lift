# openarm_lift

ROS 2 串口桥接包：通过话题控制升降臂（设置目标高度、急停、周期上报当前高度）

## 环境要求

- **ROS 2**（Humble / Jazzy / Iron 等；需已安装 `rclpy`、`std_msgs`，桌面安装一般已包含）
- **Python 3** 与 **pyserial**：`pip install pyserial`（或 `sudo apt install python3-serial`）
- 升降臂连接 **USB 转串口**，Linux 上常见设备名为 `/dev/ttyUSB0`（以实际为准）
- 用户需在 **dialout** 组或有串口读写权限，否则无法打开设备：

  ```bash
  sudo usermod -aG dialout $USER
  # 重新登录后生效
  ```

## 安装

1. 将整个 `openarm_lift` 文件夹放到自己的 Colcon 工作空间 **`src/`** 下，例如：

   ```text
   ~/ros2_ws/src/openarm_lift/
   ```

2. 在工作空间**根目录**编译并加载环境：

   ```bash
   cd ~/ros2_ws
   source /opt/ros/<你的发行版>/setup.bash   # 例: humble
   colcon build --packages-select openarm_lift
   source install/setup.bash
   ```

   使用 **zsh** 时可将最后一行改为 `source install/setup.zsh`。



## 运行节点

```bash
ros2 run openarm_lift lift_node
```

指定串口与发布频率（单位 Hz）：

```bash
ros2 run openarm_lift lift_node --ros-args -p serial_port:=/dev/ttyUSB0 -p publish_rate:=1.0
```

## 一键脚本（可选）

在包目录下：

```bash
chmod +x scripts/run_lift_node.sh  
./scripts/run_lift_node.sh
# 或带参数：
./scripts/run_lift_node.sh --ros-args -p serial_port:=/dev/ttyUSB1 -p publish_rate:=2.0
```

脚本使用 **bash** 调用 `setup.bash`。若工作空间不在默认推断路径，先设置：

```bash
export ROS2_WS=/你的/ros2_ws路径
```

## 话题说明

| 话题名 | 方向 | 消息类型 | 说明 |
|--------|------|----------|------|
| `/lift/cmd_height` | 订阅 | `std_msgs/msg/Int32` | 目标高度 **0～600** |
| `/lift/cmd_stop` | 订阅 | `std_msgs/msg/Empty` | 任意发一条即可停止运动 |
| `/lift/current_height` | 发布 | `std_msgs/msg/Int32` | 按 `publish_rate` 周期发布；**`-1` 表示本次读高度失败** |

## 快速测试（另开终端，已 `source install/setup.bash`）

```bash
# 订阅当前高度
ros2 topic echo /lift/current_height

# 设置目标高度 300
ros2 topic pub --once /lift/cmd_height std_msgs/msg/Int32 "{data: 300}"

# 停止
ros2 topic pub --once /lift/cmd_stop std_msgs/msg/Empty "{}"
```

## 交互式命令行

键盘输入高度 / `s` 查询 / `p` 停止 / `q` 退出：

```bash
ros2 run openarm_lift lift_control_cli
```

默认串口仍为 `/dev/ttyUSB0`；若需改口，请使用上面的 **`lift_node` + 参数**，或自行修改 `openarm_lift/lift_control.py` 中 `LiftArm` 的默认端口。

## 常见问题

- **找不到包**：确认已在本工作空间执行 `colcon build` 且当前终端已 `source install/setup.bash`。
- **`ModuleNotFoundError: serial`**：安装 `pyserial`。
- **Permission denied 串口**：检查 `dialout` 组与设备路径；或临时 `sudo chmod 666 /dev/ttyUSB0`（不推荐长期使用）。

## 许可

见 `package.xml` 中的 `license` 字段。
