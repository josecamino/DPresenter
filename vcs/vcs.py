import json
import os
import os.path
import sqlite3
from os.path import isfile

class VCSProject(object):
	def __init__(self, path):
		self.path = path
		self._repo = FileRepository(self)

	def get_presentation(self, presentation_id):
		return self._repo.load_presentation(presentation_id)

	def get_current_presentation(self):
		return self._repo.load_current_presentation()
		
	def get_presentation_list(self):
		return self._repo.load_presentation_list()

class Presentation(object):
	pass

class CurrentPresentation(Presentation):
	def __init__(self, project, **data):
		self.id = data.get('id', -1)
		self.name = data['name']
		self.project = project
		self._repo = project._repo
		self.slides = []

	def is_persisted(self):
		return False

	def persist(self, new_name="Untitled"):
		self._repo.persist_presentation(self, new_name)

	def add_slide(self):
		pass

	def checkout(self, slide):
		pass

	def checkin(self, slide, newData):
		pass

class PersistedPresentation(Presentation):
	def __init__(self, project, **data):
		self.id = data.get('id', -1)
		self.name = data['name']
		self.project = project
		self._repo = project._repo
		self.slides = []

	def is_persisted(self):
		return True

	def rename(self, new_name):
		pass

class FileRepository(object):
	"""
	Internal class that deals with the actual logic involved in persistence.
	TODO: Perhaps split this into a facade for actual plumbing, so that we don't have to
	keep reopening sqlite instances
	"""

	def __init__(self, project):
		self.project = project

	def make_path(self, path):
		return os.path.join(self.project.path, path)

	def load_data(self, path):
		path = self.make_path(path)
		with open(path, 'r') as file:
			return json.load(file)

	def save_data(self, path, data):
		path = self.make_path(path)
		with open(path, 'w') as file:
			json.dump(data, file)

	def connect_to_db(self):
		return sqlite3.connect(self.make_path('data.db'))

	def create_repository(self):
		# TODO: Raise if already initialized
		repository_path = self.project.path
		os.mkdir(repository_path)
		os.mkdir(os.path.join(repository_path, "slide_data"))

		with self.connect_to_db() as conn:
			c = conn.cursor()

			c.execute("""
				CREATE TABLE presentations
				(id integer primary key autoincrement, name text)
				""")

		self.create_presentation(CurrentPresentation(self.project, name="current"))

	def persist_presentation(self, current_presentation, new_name):
		"Used to add non-current presentations to the project"

		# first copy the presentation
		new_presentation = PersistedPresentation(self.project, 
			name = new_name
		)

		self.create_presentation(new_presentation)

	def create_presentation(self, presentation):
		"Creates a new presentation."
		with self.connect_to_db() as conn:
			c = conn.cursor()

			c.execute("""
				INSERT INTO presentations (name)
				VALUES (?)
				""", [presentation.name])

	def save_presentation(self, presentation):
		"Saves a presentation."

		with self.connect_to_db() as conn:
			c = conn.cursor()

			c.execute("""
				UPDATE presentations
				SET name = ?
				WHERE id = ?
				""", [presentation.id])

	def load_current_presentation(self):
		# Todo: make more efficient
		return self.load_presentation_list()[0]

	def load_presentation_list(self):
		presentations = []

		with self.connect_to_db() as conn:
			c = conn.cursor()

			c.execute("""
				SELECT id, name
				FROM presentations
				ORDER BY id ASC
				""")

			for row in c.fetchall():
				pid = row[0]
				name = row[1]

				presentation_data = {
					'id': pid,
					'name': name
				}

				if not presentations:
					presentations.append(CurrentPresentation(self.project, **presentation_data))
				else:
					presentations.append(PersistedPresentation(self.project, **presentation_data))

		return presentations

	def load_presentation(self, pid):
		with self.connect_to_db() as conn:
			c = conn.cursor()

			c.execute("""
				SELECT name
				FROM presentations
				WHERE id = ?
				""", [pid])

			data = c.fetchone()
			name = data[0]
			presentation_data = {
				'id': pid,
				'name': name
			}

			if pid == 1: # TODO: Use a non-hardcoded value that doesn't depend on sqlite implementation
				return CurrentPresentation(self.project, **presentation_data)
			else:
				return PersistedPresentation(self.project, **presentation_data) 
