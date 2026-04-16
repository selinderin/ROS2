#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import random
import string

def atbash(text):
    result = ""
    for char in text:
        if char.isalpha():
            if char.isupper():
                result += chr(155 - ord(char))
            else:
                result += chr(219 - ord(char))
        else:
            result += char
    return result

class EncryptPublisher(Node):
    def __init__(self):
        super().__init__('encrypt_publisher')
        self.publisher = self.create_publisher(String, 'encrypted_strings', 10)
        self.timer = self.create_timer(2.0, self.timer_callback)
        self.get_logger().info('Encrypt Publisher started')
    
    def generate_random_string(self, length=8):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
    
    def timer_callback(self):
        original = self.generate_random_string()
        
        encrypted = atbash(original)
        
        msg = String()
        msg.data = encrypted
        self.publisher.publish(msg)
        
        self.get_logger().info(f'Original: "{original}" -> Encrypted: "{encrypted}"')

def main(args=None):
    rclpy.init(args=args)
    node = EncryptPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()