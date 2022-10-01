from flask import jsonify, render_template, request, redirect, url_for, make_response
from app import app
from app.api_utils import bulk_upload_to_database, process_recipe_form, to_dict, search_recipe, handle_quote_of_day, process_all_projects, process_all_recipes
from app.models import Project, Recipe
from app import db
import datetime
import json

@app.route('/weight')
@app.route('/weight/add')
@app.route('/weight/search')
@app.route('/weight/delete')
@app.route('/workout')
@app.route('/workout/add')
@app.route('/workout/search')
@app.route('/workout/delete')
@app.route('/')
def home():
    return render_template('base.html',
                           page_title='Home',
                           page_description='A centralized location for \
                            little baby toogie to handle all of her things!',
                           page_content='New features can always be added, and \
                            new commits are always pushed!',
                            notform=True,
                            quote=handle_quote_of_day())

@app.route('/recipes')
def recipes():
	recipes = Recipe.query.all()
	print("RECIPES={}".format(recipes))
	recipe = None
	recipe_count_str = 'There are no recipes currently.'
	num_recipes = 0
	if len(recipes) > 0:
		recipe = recipes[len(recipes) - 1]
		num_recipes = len(recipes)
		recipe = to_dict(recipe)
		#recipe['directions'] = recipe['directions'].split(',')
		recipe_count_str = ''
		if num_recipes == 1:
			recipe_count_str = 'There is {} recipe currently.'.format(num_recipes)
		else:
			recipe_count_str = 'There are {} recipes currently.'.format(num_recipes)
	return render_template('recipes.html',
                           page_title='Recipes',
                           page_description='A place to store all of the toogie\'s \
                            favorite recipes!',
                           page_content='New recipes can be added anytime! \
                            {}'.format(recipe_count_str),
                            quote=handle_quote_of_day(),
                            notform=True,
                            recipe=recipe,
							num_recipes=num_recipes)

@app.route('/recipes/search')
def recipes_search():
	return render_template('recipes-search.html',
                            page_title='Search for a Recipe',
                            notform=False,
                            quote=handle_quote_of_day())

@app.route('/recipes/search/results', methods=['POST'])
def recipes_search_results():
	if request.method != 'POST':
		return 'Invalid use of API!'
	else:
		recipe_list = search_recipe(request.form.to_dict()) 
		print(recipe_list)
		return render_template('recipe-search-results.html',
                            page_title='Recipe Search Results',
                            notform=False,
                            quote=handle_quote_of_day(),
                            recipes=recipe_list,
                            retrieved_recipes=len(recipe_list),
                            search_params=request.form.to_dict())


@app.route('/recipes/add')
def recipes_add():
    return render_template('recipes-add.html',
                           page_title='Add a new Recipe',
                           notform=False,
                           quote=handle_quote_of_day())

@app.route('/recipes/delete')
def recipes_delete():
    current_recipes = Recipe.query.all()
    return render_template('recipes-delete.html',
                            page_title='Delete a Recipe',
                            notform=False,
                            quote=handle_quote_of_day(),
                            recipes=current_recipes)

@app.route('/recipes/update')
def recipes_update():
    current_recipes = Recipe.query.all()
    return render_template('recipes-update.html',
                            page_title='Update a Recipe',
                            notform=False,
                            quote=handle_quote_of_day(),
                            recipes=current_recipes)


@app.route('/recipes/update/recipe', methods=['POST'])
def recipes_update_content():
	if request.method != 'POST':
		return "Illegal access of member!"
	else:
		recipe = to_dict(Recipe.query.filter_by(recipe_name=request.form['recipe_name']).first())
		print(recipe)
		return render_template('recipes-update-form.html',
							page_title='Update Recipe: {}'.format(recipe['recipe_name']),
							notform=False,
							quote=handle_quote_of_day(),
							recipe=recipe)

@app.route('/api/recipes/add/recipe', methods=['POST'])
def api_add_recipe():
	if request.method != 'POST':
		return "Invalid use of API!"
	else:
		print(request.form.to_dict())
		processed_req = process_recipe_form(request.form.to_dict())
		recipe = Recipe(recipe_name=request.form['recipe_name'],
		servings=request.form['servings'],
		prep_time=request.form['prep_time'],
		cook_time=request.form['cook_time'],
		ingredients=processed_req['ingredients'],
		directions=processed_req['directions'],
		notes=request.form['notes'])
		db.session.add(recipe)
		db.session.commit()
		return redirect(url_for('recipes'))

@app.route('/api/recipes/delete/recipe', methods=['POST'])
def api_delete_recipe():
	if request.method != 'POST':
		return 'Invalid use of API!'
	else:
		print(request.form.to_dict())
		recipe = Recipe.query.filter_by(recipe_name=request.form['recipe_name']).first()
		print(recipe)
		db.session.delete(recipe)
		db.session.commit()
		return redirect(url_for('recipes'))

@app.route('/api/recipes/update/recipe', methods=['POST'])
def api_update_recipe():
	if request.method != 'POST':
		return 'Invalid use of API!'
	else:
		print(request.form.to_dict())
		recipe_d = request.form.to_dict()
		processed_req = process_recipe_form(recipe_d)
		db.session.query(Recipe). \
			filter(Recipe.recipe_name == str(recipe_d['old_recipe_name'])). \
			update({
				'recipe_name' : recipe_d['recipe_name'],
				'servings' : recipe_d['servings'],
				'prep_time' : recipe_d['prep_time'],
				'cook_time' : recipe_d['cook_time'],
				'ingredients' : processed_req['ingredients'],
				'directions' : processed_req['directions'],
				'notes' : recipe_d['notes']
			})
		db.session.commit()
		print(f)
		return redirect(url_for('recipes'))

@app.route('/projects')
def projects():
	projects = Project.query.all()
	print("Projects={}".format(recipes))
	project_count_str = 'There are no projects currently.'
	num_projects = 0
	if len(projects) > 0:
		num_projects = len(projects)
		if num_projects == 1:
			project_count_str = 'There is {} project currently.'.format(num_projects)
		else:
			project_count_str = 'There are {} projects currently.'.format(num_projects)
	return render_template('projects.html',
                           page_title='Projects',
                           page_description='A place to track all of the toogie\'s \
                            ongoing adventures and projects!',
                           page_content='New projects can be added anytime! \
                            {}'.format(project_count_str),
                            quote=handle_quote_of_day(),
                            notform=True,
							num_projects=num_projects,
							projects=projects)

@app.route('/projects/add')
def project_add():
    return render_template('projects-add.html',
                           page_title='Add a new Project',
                           notform=False,
                           quote=handle_quote_of_day())

@app.route('/projects/delete')
def project_delete():
    projects = Project.query.all()
    return render_template('projects-delete.html',
                            page_title='Delete a Recipe',
                            notform=False,
                            quote=handle_quote_of_day(),
                            projects=projects)


@app.route('/api/projects/add/project', methods=['POST'])
def api_add_project():
	if request.method != 'POST':
		return "Invalid use of API!"
	else:
		print(request.form.to_dict())
		project = Project(name=request.form['name'],
		desc=request.form['desc'],
		est_comp=request.form['est_comp'])
		db.session.add(project)
		db.session.commit()
		return redirect(url_for('projects'))

@app.route('/api/projects/delete/project', methods=['POST'])
def api_delete_project():
	if request.method != 'POST':
		return 'Invalid use of API!'
	else:
		print(request.form.to_dict())
		project = Project.query.filter_by(name=request.form['name']).first()
		print(project)
		db.session.delete(project)
		db.session.commit()
		return redirect(url_for('projects'))


@app.route('/exim')
def exim():
	return render_template('exim.html',
                            page_title='Export / Import Database',
                            notform=False,
                            quote=handle_quote_of_day())

@app.route('/api/database/import', methods=['POST'])
def import_db():
	if request.method != 'POST':
		return "Illegal use of API!"
	else:
		dbfile = request.files['dbfile']
		if dbfile:
			db_data = json.load(dbfile)
			bulk_upload_to_database(db_data)
			print(db_data)
			print(db_data.keys())
		return redirect(url_for('exim'))

@app.route('/api/database/export')
def export_db():
	recipes = process_all_recipes(Recipe.query.all())
	projects = process_all_projects(Project.query.all())
	print(recipes, ' : ', type(recipes))
	print(projects, ' : ', type(projects))
	payload = {
		'recipes' : recipes,
		'projects' : projects
	}
	response = make_response(jsonify(payload))
	now = datetime.datetime.now()
	now = now.strftime('%d_%m_%Y')
	response.headers['Content-Disposition'] = 'attachment; filename=EXPORT_{}.json'.format(now)
	response.mimetype = 'text/json'
	return response