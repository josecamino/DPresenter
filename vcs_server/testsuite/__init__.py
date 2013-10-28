import os
import os.path
import unittest
import vcs_server

import unit
from helper import remove_dir_if_exists, get_vcs

def flatten(item_list):
	return [val for sublist in item_list for val in sublist]
		
def test():
	"The main test method"
	remove_dir_if_exists("testprojects")
	os.mkdir("testprojects")
	get_vcs().set_projects_location("testprojects")

	tests = flatten([
		unit.get_tests()
	])

	loader = unittest.TestLoader()
	test_suites = [loader.loadTestsFromTestCase(case) for case in tests]
	suite = unittest.TestSuite(test_suites)
	unittest.TextTestRunner(verbosity=2).run(suite)
	
