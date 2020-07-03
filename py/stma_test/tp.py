#!/usr/bin/env python3
"""

When executed, this module represents a threat to be sensed and reported by the
agent application under test.

todo: improve command-line argument processing to handle bad or missing args

"""
import sys
import time

if __name__ == "__main__":
    sseconds = int(sys.argv[1])  # sleep seconds
    tag = sys.argv[2]
    time.sleep(sseconds)
    print(tag)
