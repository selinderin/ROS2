#!/usr/bin/env python3
import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rclpy
from robot_farmer_interfaces.action import Harvest
from robot_farmer_interfaces.srv import CollectCrop


class TestTurtleFarmer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rclpy.init(args=[])

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        from robot_farmer import turtle_farmer

        self.node = turtle_farmer.TurtleFarmer()

        # Mock the clients
        self.node.collect_client = Mock()
        self.node.teleport_client = Mock()
        self.node.action_server = Mock()

    def tearDown(self):
        if hasattr(self, 'node'):
            self.node.destroy_node()

    def test_initialization(self):
        self.assertEqual(self.node.warehouse, (1.0, 9.0))
        self.assertEqual(len(self.node.beds), 8)
        self.assertEqual(self.node.beds[1], (2.0, 2.0))
        self.assertEqual(self.node.beds[8], (8.0, 8.0))
        self.assertIsInstance(self.node.action_server, Mock)

    def test_teleport(self):
        mock_future = Mock()
        self.node.teleport_client.call_async = Mock(return_value=mock_future)

        self.node.teleport(5.0, 7.0)

        self.node.teleport_client.call_async.assert_called_once()
        args = self.node.teleport_client.call_async.call_args[0][0]
        self.assertEqual(args.x, 5.0)
        self.assertEqual(args.y, 7.0)
        self.assertEqual(args.theta, 0.0)

    @patch('rclpy.spin_until_future_complete')
    def test_collect_crop_success(self, mock_spin):
        mock_future = Mock()
        mock_result = Mock()
        mock_result.amount_collected = 42
        mock_future.result.return_value = mock_result
        self.node.collect_client.call_async = Mock(return_value=mock_future)

        amount = self.node.collect_crop(1)

        self.assertEqual(amount, 42)
        self.node.collect_client.call_async.assert_called_once()

    @patch('rclpy.spin_until_future_complete')
    def test_collect_crop_invalid_bed(self, mock_spin):
        mock_future = Mock()
        mock_result = Mock()
        mock_result.amount_collected = 0
        mock_future.result.return_value = mock_result
        self.node.collect_client.call_async = Mock(return_value=mock_future)

        amount = self.node.collect_crop(99)
        self.assertEqual(amount, 0)

    def test_execute_callback_valid_bed(self):
        mock_goal_handle = Mock()
        mock_goal_handle.request.bed_id = 1
        mock_goal_handle.publish_feedback = Mock()

        self.node.collect_crop = Mock(return_value=15)
        self.node.teleport = Mock()

        result = self.node.execute_callback(mock_goal_handle)

        self.assertEqual(self.node.teleport.call_count, 3)
        self.assertEqual(mock_goal_handle.publish_feedback.call_count, 4)
        self.assertEqual(result.total_collected, 15)
        mock_goal_handle.succeed.assert_called_once()

    def test_execute_callback_invalid_bed(self):
        mock_goal_handle = Mock()
        mock_goal_handle.request.bed_id = 99
        mock_goal_handle.publish_feedback = Mock()

        self.node.collect_crop = Mock(return_value=0)
        self.node.teleport = Mock()

        result = self.node.execute_callback(mock_goal_handle)

        self.node.collect_crop.assert_called_with(99)
        self.assertEqual(result.total_collected, 0)

    def test_execute_callback_feedback_order(self):
        from robot_farmer_interfaces.action import Harvest

        mock_goal_handle = Mock()
        mock_goal_handle.request.bed_id = 1
        mock_goal_handle.publish_feedback = Mock()

        # Create a list to capture feedback statuses in order
        captured_statuses = []

        def capture_feedback(feedback):
            captured_statuses.append(feedback.status)

        mock_goal_handle.publish_feedback.side_effect = capture_feedback

        self.node.collect_crop = Mock(return_value=10)
        self.node.teleport = Mock()

        self.node.execute_callback(mock_goal_handle)

        expected_statuses = [
            'Moving to bed 1',
            'Collecting from bed 1',
            'Delivering to warehouse',
            'Returning to start'
        ]
        self.assertEqual(captured_statuses, expected_statuses)


if __name__ == '__main__':
    unittest.main()