from django.test import TestCase

# Create your tests here.
import time

#this is a comment 
counter = 0
while True:
    time.sleep(1)
    counter += 1
    if counter > 10:
        break
