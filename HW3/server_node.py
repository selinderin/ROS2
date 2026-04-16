#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from string_sorter_srv.srv import SortStrings

class StringSorterServer(Node):
    def __init__(self):
        super().__init__('string_sorter_server')
        
        self.service = self.create_service(
            SortStrings,
            'sort_strings',
            self.sort_callback
        )
        self.get_logger().info('String Sorter Server ready')
    
    def sort_callback(self, request, response):
        strings = request.strings_to_sort
        
        sorted_strings = sorted(strings)
        
        response.sorted_strings = sorted_strings
        
        self.get_logger().info(f'Received: {strings}')
        self.get_logger().info(f'Sorted:   {sorted_strings}')
        
        return response

def main(args=None):
    rclpy.init(args=args)
    node = StringSorterServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
