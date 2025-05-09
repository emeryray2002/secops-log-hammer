"""Test cases for the generators module."""

import unittest
from unittest.mock import patch

from secops_log_hammer.generators import (
    generate_ip_address,
    generate_hostname,
    generate_username,
    generate_entities,
    fill_log_template
)


class TestGenerators(unittest.TestCase):
    """Test cases for the generator functions.
    
    This class tests the various functions in the generators module
    that create synthetic data for log generation.
    """

    def test_generate_ip_address(self) -> None:
        """Test that generate_ip_address returns a valid IPv4 address."""
        ip = generate_ip_address()
        # Check if the IP has 4 parts
        parts = ip.split('.')
        self.assertEqual(len(parts), 4, "IP address should have 4 parts")
        
        # Check each part is a valid number
        for part in parts:
            self.assertTrue(part.isdigit(), f"Part '{part}' should be a number")
            num = int(part)
            self.assertTrue(0 <= num <= 255, f"Part '{part}' should be between 0 and 255")
    
    def test_generate_hostname(self) -> None:
        """Test that generate_hostname returns a valid hostname."""
        domains = ["example.com", "test.local"]
        hostname = generate_hostname(domains)
        
        # Check if the hostname has a name and domain part
        self.assertTrue('.' in hostname, "Hostname should contain a dot")
        
        name, domain = hostname.split('.', 1)
        self.assertTrue(len(name) > 0, "Hostname name part should not be empty")
        self.assertIn(domain, domains, "Domain should be one from the provided list")
    
    def test_generate_username(self) -> None:
        """Test that generate_username returns a valid username."""
        username = generate_username()
        
        # Check that the username is not empty
        self.assertTrue(len(username) > 0, "Username should not be empty")
        
        # Check that it ends with digits (as per the function implementation)
        self.assertTrue(username[-2:].isdigit(), "Username should end with digits")
    
    def test_generate_entities(self) -> None:
        """Test that generate_entities returns the expected structure."""
        entities = generate_entities(num_hosts=3, num_ips_per_host=2, num_users=5)
        
        # Check the structure
        self.assertIn('hosts', entities, "Entities should contain 'hosts'")
        self.assertIn('ips', entities, "Entities should contain 'ips'")
        self.assertIn('users', entities, "Entities should contain 'users'")
        
        # Check the counts
        self.assertEqual(len(entities['hosts']), 3, "Should generate 3 hosts")
        self.assertEqual(len(entities['users']), 5, "Should generate 5 users")
        
        # Check that each host has 2 IPs
        for host in entities['hosts']:
            self.assertIn(host, entities['ips'], f"Host {host} should have IPs")
            self.assertEqual(len(entities['ips'][host]), 2, f"Host {host} should have 2 IPs")
    
    def test_fill_log_template(self) -> None:
        """Test that fill_log_template properly fills a template with entity data."""
        # Create a simple template for testing
        template = {
            "EventTime": None,
            "Hostname": None,
            "Message": "User {target_username} logged in from {source_ip}",
            "IpAddress": None
        }
        
        # Create simple entities for testing
        entities = {
            "hosts": ["test.example.com"],
            "ips": {"test.example.com": ["192.168.1.1"]},
            "users": ["testuser"]
        }
        
        # Test with fixed values for time
        current_time_ms = 1600000000000
        current_time_iso = "2020-09-13T12:26:40Z"
        
        filled_log = fill_log_template(
            template, 
            entities, 
            "customer123", 
            "project456",
            "WINEVTLOG",
            current_time_ms, 
            current_time_iso
        )
        
        # Check that fields were filled
        self.assertEqual(filled_log["EventTime"], current_time_ms)
        self.assertEqual(filled_log["Hostname"], "test.example.com")
        self.assertEqual(filled_log["IpAddress"], "192.168.1.1")
        
        # Check that the message was interpolated
        self.assertIn("User testuser logged in from 192.168.1.1", filled_log["Message"])


if __name__ == '__main__':
    unittest.main() 