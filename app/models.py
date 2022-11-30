from app import db

		
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
	tstamp = db.Column(db.String)

class Quote(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String)
	quote = db.Column(db.String)
	fetched_on = db.Column(db.String)

class Food_Diary(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	breakfast = db.Column(db.String)
	b_cal = db.Column(db.REAL)
	lunch = db.Column(db.String)
	l_cal = db.Column(db.REAL)
	dinner = db.Column(db.String)
	d_cal = db.Column(db.REAL)
	snack = db.Column(db.String)
	s_cal = db.Column(db.REAL)
	tstamp = db.Column(db.String)

class Book(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	isbn = db.Column(db.String)
	title = db.Column(db.String)
	author = db.Column(db.String)
	owned = db.Column(db.String)
	have_read = db.Column(db.String)
	rating = db.Column(db.Integer)
	tags = db.Column(db.String)
	is_series = db.Column(db.String)
	no_in_series = db.Column(db.Integer)

	def __repr__(self):
		return self.title
