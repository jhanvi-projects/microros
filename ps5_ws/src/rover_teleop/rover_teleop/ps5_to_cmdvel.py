#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist


class PS5ToCmdVel(Node):

    def __init__(self):

        super().__init__('ps5_to_cmdvel')

        # ====================================================
        # /joy SUBSCRIBER
        # ====================================================

        self.joy_subscriber = self.create_subscription(
            Joy,
            '/joy',
            self.joy_callback,
            10
        )

        # ====================================================
        # /cmd_vel PUBLISHER
        # ====================================================

        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # ====================================================
        # ROBOT SPEED
        # ====================================================

        self.max_linear_speed = 0.5
        self.max_angular_speed = 0.5

        # ====================================================
        # PS5 AXES
        #
        # Based on YOUR controller:
        #
        # Left stick up/down  -> axis 1
        # Left stick left/right -> axis 0
        # Right stick left/right -> axis 3
        # ====================================================

        self.axis_forward = 1
        self.axis_strafe = 0
        self.axis_rotate = 3

        # ====================================================
        # DEADZONE
        # ====================================================

        self.deadzone = 0.08

        # ====================================================
        # STORED VALUES
        # ====================================================

        self.linear_x = 0.0
        self.linear_y = 0.0
        self.angular_z = 0.0

        # ====================================================
        # PUBLISH AT 20 Hz
        # ====================================================

        self.timer = self.create_timer(
            0.05,
            self.publish_cmd_vel
        )

        self.get_logger().info(
            'PS5 -> /cmd_vel started'
        )

    # ========================================================
    # DEADZONE FUNCTION
    # ========================================================

    def apply_deadzone(self, value):

        if abs(value) < self.deadzone:
            return 0.0

        return value

    # ========================================================
    # JOYSTICK CALLBACK
    # ========================================================

    def joy_callback(self, msg):

        if len(msg.axes) <= self.axis_rotate:
            return

        # ----------------------------------------------------
        # Read controller
        # ----------------------------------------------------

        forward = msg.axes[self.axis_forward]

        strafe = msg.axes[self.axis_strafe]

        rotate = msg.axes[self.axis_rotate]


        # ----------------------------------------------------
        # Apply deadzone
        # ----------------------------------------------------

        forward = self.apply_deadzone(forward)

        strafe = self.apply_deadzone(strafe)

        rotate = self.apply_deadzone(rotate)


        # ----------------------------------------------------
        # Forward direction
        #
        # Your controller gives:
        #
        # stick UP = +1
        # stick DOWN = -1
        #
        # So DON'T invert it here.
        # ----------------------------------------------------

        self.linear_x = forward

        self.linear_y = strafe

        self.angular_z = rotate

    # ========================================================
    # PUBLISH CMD_VEL
    # ========================================================

    def publish_cmd_vel(self):

        cmd = Twist()


        # ----------------------------------------------------
        # Linear X
        # ----------------------------------------------------

        cmd.linear.x = (
            self.linear_x *
            self.max_linear_speed
        )


        # ----------------------------------------------------
        # Linear Y
        # ----------------------------------------------------

        cmd.linear.y = (
            self.linear_y *
            self.max_linear_speed
        )


        cmd.linear.z = 0.0


        # ----------------------------------------------------
        # Angular
        # ----------------------------------------------------

        cmd.angular.x = 0.0

        cmd.angular.y = 0.0

        cmd.angular.z = (
            self.angular_z *
            self.max_angular_speed
        )


        # ----------------------------------------------------
        # Publish
        # ----------------------------------------------------

        self.cmd_vel_publisher.publish(cmd)


def main(args=None):

    rclpy.init(args=args)

    node = PS5ToCmdVel()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        # ----------------------------------------------------
        # Send final STOP command
        # ----------------------------------------------------

        stop = Twist()

        node.cmd_vel_publisher.publish(stop)

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':

    main()
