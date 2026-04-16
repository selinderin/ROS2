import unittest
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from pair_finder_action.action import FindPairs

class TestPairFinderAction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()
        cls.node = Node('test_action_client')
        cls.client = ActionClient(cls.node, FindPairs, 'find_pairs')
        cls.client.wait_for_server()
        cls.received_feedback = []

    @classmethod
    def tearDownClass(cls):
        cls.node.destroy_node()
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        self.received_feedback.append(list(feedback_msg.feedback.current_pair))

    def send_goal_and_wait(self, numbers):
        self.received_feedback = []
        goal = FindPairs.Goal()
        goal.numbers = numbers
        future = self.client.send_goal_async(goal, feedback_callback=self.feedback_callback)
        rclpy.spin_until_future_complete(self.node, future)
        goal_handle = future.result()
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self.node, result_future)
        return result_future.result().result

    def test_even_number_of_elements(self):
        numbers = [5, 1, 8, 2, 9, 3]
        result = self.send_goal_and_wait(numbers)
        expected_pairs = [1, 2, 3, 5, 8, 9]
        self.assertEqual(list(result.pairs), expected_pairs)

    def test_odd_number_of_elements(self):
        numbers = [5, 1, 8, 2, 9]
        result = self.send_goal_and_wait(numbers)
        expected_pairs = [1, 2, 5, 8, 9, 0]
        self.assertEqual(list(result.pairs), expected_pairs)

    def test_single_element(self):
        numbers = [7]
        result = self.send_goal_and_wait(numbers)
        expected_pairs = [7, 0]
        self.assertEqual(list(result.pairs), expected_pairs)

    def test_two_elements(self):
        numbers = [10, 20]
        result = self.send_goal_and_wait(numbers)
        expected_pairs = [10, 20]
        self.assertEqual(list(result.pairs), expected_pairs)

    def test_feedback_is_sent(self):
        numbers = [5, 1, 8, 2, 9, 3]
        self.send_goal_and_wait(numbers)
        self.assertGreater(len(self.received_feedback), 0)

    def test_correct_pairs_order(self):
        numbers = [10, 1, 5, 2]
        self.send_goal_and_wait(numbers)
        expected_feedback = [[1, 2], [5, 10]]
        for i, expected in enumerate(expected_feedback):
            if i < len(self.received_feedback):
                self.assertEqual(self.received_feedback[i], expected)

    def test_empty_array(self):
        numbers = []
        result = self.send_goal_and_wait(numbers)
        expected_pairs = []
        self.assertEqual(list(result.pairs), expected_pairs)

if __name__ == '__main__':
    unittest.main()
