from setuptools import find_packages, setup

package_name = 'openarm_lift'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='OpenArm',
    maintainer_email='openarm_dev@enactic.ai',
    description='ROS 2 serial bridge for OpenArm lift.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'lift_node = openarm_lift.lift_node:main',
            'lift_control_cli = openarm_lift.lift_control:cli_main',
        ],
    },
)
