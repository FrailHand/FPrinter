import unittest

import os
import sys
sys.path.append(os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.realpath(__file__)))))

import fprinter.backend.drivers as drivers

class TestDummyDriver(unittest.TestCase):

    def test_normal(self):
        '''test function dummy with no stupid flag'''

        # we check that the output is equal to the input of the dummy function
        self.assertEqual(drivers.dummy('test_input'), 'test_input')

    def test_stupid(self):
        '''test function with stupid flag'''
        self.assertEqual(drivers.dummy('test_input', stupid=True), None)

    # it is important that all the test function names begin with 'test'
    def test_fail(self):
        '''this is a test that will fail on the dummy function'''

        # here the test fails because the output is not the predicted one
        self.assertEqual(drivers.dummy('test_input'), 'wrong_output')



if __name__=='__main__':
    print('\nRunning unittest on backend\n')
    unittest.main()
