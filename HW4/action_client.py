#!/usr/bin/env python3
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from pair_finder_action.action import FindPairs

class PairFinderClient(Node):
    def __init__(self):
        super().__init__('pair_finder_client')
        self.client = ActionClient(self, FindPairs, 'find_pairs')
        self.get_logger().info('Client is ready')
    
    def send_numbers(self, numbers):
        self.client.wait_for_server()
        
        goal = FindPairs.Goal()
        goal.numbers = numbers
        
        self.get_logger().info(f'Sending: {numbers}')
        future = self.client.send_goal_async(goal, feedback_callback=self.feedback_callback)
        future.add_done_callback(self.goal_done)
    
    def feedback_callback(self, feedback_msg):
        pair = feedback_msg.feedback.current_pair
        self.get_logger().info(f'Got feedback: {pair}')
    
    def goal_done(self, future):
        goal_handle = future.result()
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)
    
    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Final result: {result.pairs}')
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    client = PairFinderClient()
    
    numbers = [5, 1, 8, 2, 9, 3, 7]
    client.send_numbers(numbers)
    
    rclpy.spin(client)

if __name__ == '__main__':
    main()