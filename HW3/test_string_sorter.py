import unittest
import rclpy
from rclpy.node import Node
from string_sorter_srv.srv import SortStrings

class TestStringSorterService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()
        cls.node = Node('test_client')
        cls.client = cls.node.create_client(SortStrings, 'sort_strings')
        while not cls.client.wait_for_service(timeout_sec=1.0):
            pass

    @classmethod
    def tearDownClass(cls):
        cls.node.destroy_node()
        rclpy.shutdown()

    def test_sort_basic_array(self):
        request = SortStrings.Request()
        request.strings_to_sort = ["bad", "and", "good"]
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self.node, future)
        result = future.result()
        self.assertEqual(result.sorted_strings, ["and", "bad", "good"])

    def test_sort_already_sorted(self):
        request = SortStrings.Request()
        request.strings_to_sort = ["a", "b", "c"]
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self.node, future)
        result = future.result()
        self.assertEqual(result.sorted_strings, ["a", "b", "c"])

    def test_sort_reverse_order(self):
        request = SortStrings.Request()
        request.strings_to_sort = ["zebra", "yak", "xray"]
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self.node, future)
        result = future.result()
        self.assertEqual(result.sorted_strings, ["xray", "yak", "zebra"])

    def test_sort_with_duplicates(self):
        request = SortStrings.Request()
        request.strings_to_sort = ["cat", "alien", "cat", "book"]
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self.node, future)
        result = future.result()
        self.assertEqual(result.sorted_strings, ["alien", "book", "cat", "cat"])

    def test_sort_empty_array(self):
        request = SortStrings.Request()
        request.strings_to_sort = []
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self.node, future)
        result = future.result()
        self.assertEqual(result.sorted_strings, [])

    def test_sort_single_element(self):
        request = SortStrings.Request()
        request.strings_to_sort = ["hello"]
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self.node, future)
        result = future.result()
        self.assertEqual(result.sorted_strings, ["hello"])

if __name__ == '__main__':
    unittest.main()
