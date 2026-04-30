import rclpy
from rclpy.node import Node
from std_msgs.msg import Empty, Int32

from openarm_lift.lift_control import LiftArm


class LiftArmNode(Node):
    """ROS 2 bridge: same behavior as CLI (set height, stop, read height)."""

    def __init__(self):
        super().__init__('lift_arm')
        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('publish_rate', 1.0)

        port = self.get_parameter('serial_port').get_parameter_value().string_value
        rate = self.get_parameter('publish_rate').get_parameter_value().double_value
        if rate <= 0.0:
            rate = 1.0

        self._arm = LiftArm(port=port, verbose=False)
        self._pub = self.create_publisher(Int32, 'lift/current_height', 10)
        self.create_subscription(Int32, 'lift/cmd_height', self._on_cmd_height, 10)
        self.create_subscription(Empty, 'lift/cmd_stop', self._on_cmd_stop, 10)

        period = 1.0 / rate
        self.create_timer(period, self._timer_publish_height)

        self.get_logger().info(
            f'Lift ready (port={port}). Topics: lift/cmd_height, lift/cmd_stop, '
            f'lift/current_height @ {rate} Hz'
        )

    def _on_cmd_height(self, msg: Int32):
        self._arm.go_to_height(int(msg.data))

    def _on_cmd_stop(self, _msg: Empty):
        self._arm.stop()

    def _timer_publish_height(self):
        h = self._arm.get_current_height(silent=True)
        out = Int32()
        out.data = -1 if h is None else int(h)
        self._pub.publish(out)


def main():
    rclpy.init()
    node = LiftArmNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node._arm.close()
        node.destroy_node()
        rclpy.shutdown()
