import unittest

import os
import sys
sys.path.append(os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.realpath(__file__)))))

import fprinter

if __name__=='__main__':
    print('\nRunning unittest on backend\n')
    unittest.main()
