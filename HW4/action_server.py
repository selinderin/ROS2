#!/usr/bin/env python3
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from pair_finder_action.action import FindPairs

class PairFinderServer(Node):
    def __init__(self):
        super().__init__('pair_finder_server')
        self.server = ActionServer(
            self,
            FindPairs,
            'find_pairs',
            self.execute_callback
        )
        self.get_logger().info('Server is ready')
    
    def find_pair_with_smallest_sum(self, numbers):
        min_sum = None
        pair = None
        
        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                total = numbers[i] + numbers[j]
                
                if min_sum is None or total < min_sum:
                    min_sum = total
                    pair = (min(numbers[i], numbers[j]), max(numbers[i], numbers[j]))
        
        return pair
    
    def execute_callback(self, goal_handle):
        numbers = goal_handle.request.numbers
        self.get_logger().info(f'Starting with: {numbers}')
        
        all_pairs = []
        
        while len(numbers) > 0:
            if len(numbers) == 1:
                pair = (numbers[0], 0)
                numbers.pop(0)
                
                feedback = FindPairs.Feedback()
                feedback.current_pair = [pair[0], pair[1]]
                goal_handle.publish_feedback(feedback)
                self.get_logger().info(f'Feedback: {pair}')
                
                all_pairs.append(pair[0])
                all_pairs.append(pair[1])
            
            else:
                pair = self.find_pair_with_smallest_sum(numbers)
                self.get_logger().info(f'Found pair: {pair}')
                
                numbers.remove(pair[0])
                numbers.remove(pair[1])
                
                feedback = FindPairs.Feedback()
                feedback.current_pair = [pair[0], pair[1]]
                goal_handle.publish_feedback(feedback)
                self.get_logger().info(f'Feedback: {pair}')
                
                all_pairs.append(pair[0])
                all_pairs.append(pair[1])
        
        result = FindPairs.Result()
        result.pairs = all_pairs
        goal_handle.succeed()
        self.get_logger().info(f'Done! Final pairs: {all_pairs}')
        
        return result

def main(args=None):
    rclpy.init(args=args)
    server = PairFinderServer()
    rclpy.spin(server)

if __name__ == '__main__':
    main()