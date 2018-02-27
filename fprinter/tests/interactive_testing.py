import unittest

import os
import sys
sys.path.append(os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.realpath(__file__)))))

import fprinter.backend.drivers as drivers

def interactive_check(test, message):
    '''Ask the user for a confirmation check by pressing enter if OK or ^C if not'''
    answer = input('\nConfirm ([y]/n) that:\n\t{}\t'.format(message))
    print()

    test.assertIn(answer,  ['Y', 'y', ''])

class TestDummyDriver(unittest.TestCase):

    def test_stupid(self):
        '''test function dummy with stupid flag'''
        drivers.dummy('coucou', stupid=True)
        interactive_check(self, 'the screen shows "You are stupid!!"')


if __name__=='__main__':
    print('\nRunning interactive unittest on backend\n')
    unittest.main()
