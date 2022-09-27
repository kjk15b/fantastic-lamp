from app import db

class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(200))
	complete = db.Column(db.Boolean)
	
	def __repr__(self):
		return self.text
		
class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200))
	desc = db.Column(db.String(200))
	est_comp = db.Column(db.String(200))
	
	def __repr__(self):
		return self.name
		
		
class Recipe(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	recipe_name = db.Column(db.String)
	servings = db.Column(db.String)
	prep_time = db.Column(db.String)
	cook_time = db.Column(db.String)
	ingredients = db.Column(db.String)
	directions = db.Column(db.String)
	notes = db.Column(db.String)

	def __repr__(self):
		return self.recipe_name

class Weight(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	weight = db.Column(db.REAL)
	tstamp = db.Column(db.String)

class Workout(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	dur = db.Column(db.Integer)
	tstamp = db.column(db.String)

class Quote(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String)
	quote = db.Column(db.String)
	fetched_on = db.Column(db.String)