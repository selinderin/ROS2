#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from string_sorter_srv.srv import SortStrings

class StringSorterClient(Node):
    def __init__(self):
        super().__init__('string_sorter_client')
        self.client = self.create_client(SortStrings, 'sort_strings')
        
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for server...')
        self.get_logger().info('Connected to server')
    
    def send_request(self, strings):
        request = SortStrings.Request()
        request.strings_to_sort = strings
        
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None:
            response = future.result()
            return response.sorted_strings
        else:
            self.get_logger().error('Service call failed')
            return None

def main(args=None):
    rclpy.init(args=args)
    node = StringSorterClient()
    
    strings = ["class", "ros", "robotics", "nodes", "server", "client"]
    node.get_logger().info(f'Original: {strings}')
    
    result = node.send_request(strings)
    
    if result:
        node.get_logger().info(f'Sorted:   {result}')
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
