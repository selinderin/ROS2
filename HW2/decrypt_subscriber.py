#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

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

class DecryptSubscriber(Node):
    def __init__(self):
        super().__init__('decrypt_subscriber')
        
        self.subscription = self.create_subscription(
            String,
            'encrypted_strings',
            self.listener_callback,
            10)
        
        self.publisher = self.create_publisher(String, 'decrypted_strings', 10)
        
        self.get_logger().info('Decrypt Subscriber started')
    
    def listener_callback(self, msg):
        encrypted = msg.data
        
        decrypted = atbash(encrypted)
        
        decrypted_msg = String()
        decrypted_msg.data = decrypted
        self.publisher.publish(decrypted_msg)
        
        self.get_logger().info(f'Received encrypted: "{encrypted}" -> Decrypted: "{decrypted}"')

def main(args=None):
    rclpy.init(args=args)
    node = DecryptSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()