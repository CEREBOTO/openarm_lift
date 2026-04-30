import serial
import struct
import time


def crc16(data: bytes) -> bytes:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)


class LiftArm:
    def __init__(self, port: str = '/dev/ttyUSB0', verbose: bool = True):
        self._verbose = verbose
        self.ser = serial.Serial(
            port, 9600, bytesize=8, parity='N', stopbits=1, timeout=1.0
        )
        self.MAX_HEIGHT = 600
        if self._verbose:
            print('升降臂控制器已连接')
            current = self.get_current_height(silent=True)
            print(f'初始高度：{current if current is not None else "未知"}\n')
            print('操作说明：')
            print('  • 直接输入数字 → 设置目标高度 (0-600)')
            print('  • s → 查询当前高度')
            print('  • p → 停止运动')
            print('  • q → 退出\n')

    def _send(self, packet: bytes):
        self.ser.write(packet)
        self.ser.flush()
        time.sleep(0.7)
        return self.ser.read(32)

    def go_to_height(self, target: int):
        height = max(0, min(target, self.MAX_HEIGHT))
        if height != target and self._verbose:
            print(f'⚠️ 高度限制为 {height}')
        cmd = struct.pack('>BBHH', 0x01, 0x06, 0x0002, height)
        packet = cmd + crc16(cmd)
        if self._verbose:
            print(f'设置高度 → {height}')
        self._send(packet)

    def stop(self):
        cmd = bytes([0x01, 0x06, 0x00, 0x01, 0x00, 0x01])
        packet = cmd + crc16(cmd)
        if self._verbose:
            print('停止运动')
        self._send(packet)

    def get_current_height(self, silent=False):
        cmd = bytes([0x01, 0x03, 0x00, 0x02, 0x00, 0x01])
        packet = cmd + crc16(cmd)
        resp = self._send(packet)
        if resp and len(resp) >= 5 and resp[1] == 0x03:
            height = struct.unpack('>H', resp[3:5])[0]
            if not silent and self._verbose:
                print(f'当前高度：{height}')
            return height
        if not silent and self._verbose:
            print('读取失败')
        return None

    def close(self):
        self.ser.close()
        if self._verbose:
            print('串口已关闭')


def cli_main():
    arm = LiftArm()
    try:
        while True:
            cmd = input('命令 > ').strip().lower()
            if cmd in ['q', 'quit', 'exit']:
                break
            elif cmd in ['p', 'stop', '停止']:
                arm.stop()
            elif cmd in ['s', 'status', '查询']:
                arm.get_current_height()
            else:
                try:
                    height = int(cmd)
                    arm.go_to_height(height)
                except ValueError:
                    print('请输入数字、s、p 或 q')
    except KeyboardInterrupt:
        print('\n用户中断')
    finally:
        arm.close()


if __name__ == '__main__':
    cli_main()
