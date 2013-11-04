import os
import os.path
import unittest

import vcs
from helper import remove_test_repo, get_vcs

vcs = get_vcs()

def get_tests():
	return (
		TestCreateProject,
		TestLoadProject,
		TestProject,
		TestPresentation)

class TestCreateProject(unittest.TestCase):
	def setUp(self):
		remove_test_repo()
		
	def tearDown(self):
		remove_test_repo()
		
	def test_create_creates_directory(self):
		"Test that the create call succeeded"
		vcs.create_project("testrepo")
		self.assertTrue(os.path.exists("testprojects/testrepo"))

	def test_create_raises_if_exists(self):
		"Projects must have unique names"
		vcs.create_project("testrepo")
		with self.assertRaises(Exception) as ex:
			vcs.create_project("testrepo")
		
class TestLoadProject(unittest.TestCase):
	def setUp(self):
		remove_test_repo()
		vcs.create_project("testrepo")
		
	def tearDown(self):
		remove_test_repo()
		
	def test_load_raises_if_does_not_exist(self):
		remove_test_repo()
		with self.assertRaises(Exception) as ex:
			vcs.load_project("testrepo")
			
	def test_load_succeeds_if_exists(self):
		repo = vcs.load_project("testrepo")
		self.assertIsNotNone(repo)

class TestProject(unittest.TestCase):
	"Test the VCSProject object"

	def setUp(self):
		remove_test_repo() # exceptions may cause tearDown to fail
		self.project = vcs.create_project("testrepo")

	def tearDown(self):
		remove_test_repo()

	def test_get_presentation(self):
		self.project.get_current_presentation().persist("TESTVAL")
		lastId = self.project.get_presentation_list()[-1].id
		self.assertEqual(self.project.get_presentation(lastId).name, "TESTVAL")
		
	def test_get_current_presentation(self):
		"Test that get_current_presentation does return the current presentation"
		presentation = self.project.get_current_presentation()
		self.assertFalse(presentation.is_persisted())

	def test_project_start_with_one_presentation(self):
		self.assertEqual(len(self.project.get_presentation_list()), 1)

	def test_first_presentation_is_current(self):
		self.project.get_current_presentation().persist()
		self.project.get_current_presentation().persist()

		first_presentation = self.project.get_presentation_list()[0]
		self.assertFalse(first_presentation.is_persisted())

class TestPresentation(unittest.TestCase):
	def setUp(self):
		remove_test_repo()
		self.project = vcs.create_project("testrepo")
		self.presentation = self.project.get_current_presentation()

	def tearDown(self):
		remove_test_repo()

	def test_persisting_adds_a_presentation(self):
		self.presentation.persist()
		self.assertEqual(len(self.project.get_presentation_list()), 2)

	def test_persisting_with_name_sets_presentation_name(self):
		self.presentation.persist("testName")
		self.assertEqual(self.project.get_presentation_list()[1].name, "testName")

	def test_persist_returns_new_slide_id(self):
		saved_id = self.presentation.persist("testName")
		saved_presentation = self.project.get_presentation(saved_id)		
		self.assertEqual(saved_presentation.name, "testName")

	def test_persisting_keeps_the_same_slides(self):
		self.presentation.add_slide()
		self.presentation.add_slide()
		self.presentation.add_slide()

		saved_id = self.presentation.persist()
		saved_presentation = self.project.get_presentation(saved_id)
		self.assertEqual(len(saved_presentation.get_slides()), 3)

	def test_can_persist_many_presentations(self):
		self.presentation.persist()
		self.presentation.persist()
		self.presentation.persist()
		self.assertEqual(len(self.project.get_presentation_list()), 4)

	def test_renaming_presentations(self):
		saved_presentation = self.project.get_presentation(self.presentation.persist())
		saved_presentation.rename("testrename")
		self.assertEqual(saved_presentation.name, "testrename")
		self.assertEqual(self.project.get_presentation(saved_presentation.id).name, "testrename")

	def test_a_presentation_starts_with_zero_slides(self):
		self.assertEqual(len(self.presentation.get_slides()), 0)

	def test_add_slide(self):
		self.presentation.add_slide()
		self.assertEqual(len(self.presentation.get_slides()), 1)

	def test_cannot_checkout_twice(self):
		pass

	def test_checkin_works_after_checkout(self):
		pass

	def test_checkin_fails_before_checkout(self):
		pass