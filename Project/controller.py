#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from robot_farmer_interfaces.action import Harvest
from robot_farmer_interfaces.msg import CropStatus


class FarmerController(Node):
    def __init__(self):
        super().__init__('farmer_controller')

        self.action_client = ActionClient(self, Harvest, 'harvest')

        self.subscription = self.create_subscription(
            CropStatus,
            'crop_status',
            self.status_callback,
            10
        )

        self.bed_status = {}
        self.get_logger().info('Controller started')

    def status_callback(self, msg):
        self.bed_status[msg.bed_id] = msg.crop_amount

        for bed_id, amount in self.bed_status.items():
            if amount > 0:
                self.harvest_bed(bed_id)
                break

    def harvest_bed(self, bed_id):
        self.get_logger().info(f'Sending harvest goal for bed {bed_id}')

        goal = Harvest.Goal()
        goal.bed_id = bed_id

        self.action_client.wait_for_server()
        self.action_client.send_goal_async(goal, feedback_callback=self.feedback_callback)

    def feedback_callback(self, feedback_msg):
        self.get_logger().info(f'Feedback: {feedback_msg.feedback.status}')


def main(args=None):
    rclpy.init(args=args)
    node = FarmerController()
    rclpy.spin(node)


if __name__ == '__main__':
    main()