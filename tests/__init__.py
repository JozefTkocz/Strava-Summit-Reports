import sys, os

# append src directory to path to allow tests to run locally
test_dir = os.path.dirname(__file__)
src_dir = os.path.join(os.pardir, 'src')
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))
