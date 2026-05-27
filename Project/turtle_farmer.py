#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from geometry_msgs.msg import Pose
from turtlesim.srv import TeleportAbsolute
from robot_farmer_interfaces.action import Harvest
from robot_farmer_interfaces.srv import CollectCrop
import math


class TurtleFarmer(Node):
    def __init__(self):
        super().__init__('turtle_farmer')

        self.warehouse = (1.0, 9.0)

        self.beds = {
            1: (2.0, 2.0), 2: (4.0, 2.0), 3: (6.0, 2.0), 4: (8.0, 2.0),
            5: (2.0, 8.0), 6: (4.0, 8.0), 7: (6.0, 8.0), 8: (8.0, 8.0)
        }

        self.action_server = ActionServer(
            self,
            Harvest,
            'harvest',
            self.execute_callback
        )

        self.collect_client = self.create_client(CollectCrop, 'collect_crop')

        self.teleport_client = self.create_client(TeleportAbsolute, 'turtle1/teleport_absolute')

        self.get_logger().info('Turtle Farmer started')

    def teleport(self, x, y):
        req = TeleportAbsolute.Request()
        req.x = x
        req.y = y
        req.theta = 0.0
        self.teleport_client.call_async(req)

    def collect_crop(self, bed_id):
        req = CollectCrop.Request()
        req.bed_id = bed_id
        future = self.collect_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result().amount_collected

    def execute_callback(self, goal_handle):
        bed_id = goal_handle.request.bed_id

        self.get_logger().info(f'Starting harvest for bed {bed_id}')

        feedback = Harvest.Feedback()
        feedback.status = f'Moving to bed {bed_id}'
        feedback.current_crop = 0
        goal_handle.publish_feedback(feedback)

        if bed_id in self.beds:
            x, y = self.beds[bed_id]
            self.teleport(x, y)

        feedback.status = f'Collecting from bed {bed_id}'
        goal_handle.publish_feedback(feedback)

        amount = self.collect_crop(bed_id)

        feedback.status = 'Delivering to warehouse'
        goal_handle.publish_feedback(feedback)

        self.teleport(self.warehouse[0], self.warehouse[1])

        feedback.status = 'Returning to start'
        goal_handle.publish_feedback(feedback)

        self.teleport(2.0, 2.0)

        result = Harvest.Result()
        result.total_collected = amount
        goal_handle.succeed()

        self.get_logger().info(f'Completed harvest for bed {bed_id}, collected {amount}')

        return result


def main(args=None):
    rclpy.init(args=args)
    node = TurtleFarmer()
    rclpy.spin(node)


if __name__ == '__main__':
    main()