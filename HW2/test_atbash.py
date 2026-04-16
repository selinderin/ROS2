import time
import unittest
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from my_py_pkg.encrypt_publisher import atbash
from my_py_pkg.decrypt_subscriber import atbash as decrypt_atbash

class TestAtbashCipher(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def test_atbash_encrypt_lowercase(self):
        self.assertEqual(atbash("abc"), "zyx")
        self.assertEqual(atbash("hello"), "svool")
        self.assertEqual(atbash("ros"), "ilh")

    def test_atbash_encrypt_mixed(self):
        self.assertEqual(atbash("Ros2"), "Ilh2")

    def test_atbash_decrypt_same_as_encrypt(self):
        original = "hello"
        encrypted = atbash(original)
        decrypted = decrypt_atbash(encrypted)
        self.assertEqual(original, decrypted)

    def test_atbash_palindrome(self):
        self.assertEqual(atbash("svool"), "hello")

class TestTopicCommunication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()
        cls.node = Node('test_node')

    @classmethod
    def tearDownClass(cls):
        cls.node.destroy_node()
        rclpy.shutdown()

    def wait_for_topic(self, topic_name, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            topics = self.node.get_topic_names_and_types()
            topic_names = [t[0] for t in topics]
            if topic_name in topic_names:
                return True
            time.sleep(0.5)
        return False

    def test_encrypted_topic_exists(self):
        result = self.wait_for_topic('/encrypted_strings')
        self.assertTrue(result, "Topic /encrypted_strings not found")

    def test_decrypted_topic_exists(self):
        result = self.wait_for_topic('/decrypted_strings')
        self.assertTrue(result, "Topic /decrypted_strings not found")

if __name__ == '__main__':
    unittest.main()