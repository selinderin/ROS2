#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray
from robot_farmer_interfaces.msg import CropStatus
from robot_farmer_interfaces.srv import CollectCrop


class GardenManager(Node):
    def __init__(self):
        super().__init__('garden_manager')

        self.beds = {
            1: {'x': 2.0, 'y': 2.0, 'crop': 3},
            2: {'x': 4.0, 'y': 2.0, 'crop': 3},
            3: {'x': 6.0, 'y': 2.0, 'crop': 3},
            4: {'x': 8.0, 'y': 2.0, 'crop': 3},
            5: {'x': 2.0, 'y': 8.0, 'crop': 3},
            6: {'x': 4.0, 'y': 8.0, 'crop': 3},
            7: {'x': 6.0, 'y': 8.0, 'crop': 3},
            8: {'x': 8.0, 'y': 8.0, 'crop': 3},
        }

        self.status_pub = self.create_publisher(CropStatus, 'crop_status', 10)

        self.collect_srv = self.create_service(CollectCrop, 'collect_crop', self.collect_crop_callback)

        self.growth_timer = self.create_timer(10.0, self.grow_crops)

        self.status_timer = self.create_timer(1.0, self.publish_status)

        self.get_logger().info('Garden Manager started')

    def grow_crops(self):
        for bed_id in self.beds:
            if self.beds[bed_id]['crop'] < 5:
                self.beds[bed_id]['crop'] += 1
                self.get_logger().info(f'Bed {bed_id} grew to {self.beds[bed_id]["crop"]}')

    def publish_status(self):
        for bed_id, info in self.beds.items():
            msg = CropStatus()
            msg.bed_id = bed_id
            msg.crop_amount = info['crop']
            msg.x = info['x']
            msg.y = info['y']
            self.status_pub.publish(msg)

    def collect_crop_callback(self, request, response):
        bed_id = request.bed_id

        if bed_id not in self.beds:
            response.amount_collected = 0
            return response

        amount = self.beds[bed_id]['crop']
        response.amount_collected = amount
        self.beds[bed_id]['crop'] = 0

        self.get_logger().info(f'Collected {amount} from bed {bed_id}')
        return response


def main(args=None):
    rclpy.init(args=args)
    node = GardenManager()
    rclpy.spin(node)


if __name__ == '__main__':
    main()