from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        output='screen'
    )

    ps5_node = Node(
        package='rover_teleop',
        executable='ps5_to_cmdvel',
        name='ps5_to_cmdvel',
        output='screen'
    )

    return LaunchDescription([
        joy_node,
        ps5_node
    ])