from flask import jsonify, render_template, Response, request, redirect, url_for, make_response
from app import app
from app.api_utils import bulk_upload_to_database, get_past_week, get_weights_by_time, process_all_diaries, process_all_weights, process_food_diary, process_recipe_form, to_dict, search_recipe, handle_quote_of_day, process_all_projects, process_all_recipes
from app.models import Project, Recipe, Weight, Food_Diary, Book
from app import db
import datetime
import json
from io import BytesIO
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas



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
							num_recipes=num_recipes, recipe_list=recipes)

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

@app.route('/recipe/view/', methods=['POST'])
def recipe_view():
	if request.method == 'POST':
		recipe = to_dict(Recipe.query.filter_by(recipe_name=request.form['recipe_name']).first())
		search_params = {
			'cook_time' : request.form['cook_time'],
			'prep_time' : request.form['prep_time'],
			'servings' : request.form['servings'],
			'ingredients' : request.form['ingredients']
		}
		return render_template('recipe-view.html',
								page_title="Recipe Snapshot",
								quote=handle_quote_of_day(),
								search_params=search_params,
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
	weights = process_all_weights(Weight.query.all())
	food_diaries = process_all_diaries(Food_Diary.query.all())
	books = book_to_dict(Book.query.all())
	print(recipes, ' : ', type(recipes))
	print(projects, ' : ', type(projects))
	print(weights, ' : ', type(weights))
	print(books, ' : ', type(books))
	payload = {
		'recipes' : recipes,
		'projects' : projects,
		'weights' : weights,
		'food_diary' : food_diaries,
		'books' : books
	}
	response = make_response(jsonify(payload))
	now = datetime.datetime.now()
	now = now.strftime('%d_%m_%Y')
	response.headers['Content-Disposition'] = 'attachment; filename=EXPORT_{}.json'.format(now)
	response.mimetype = 'text/json'
	return response

@app.route('/weight', methods=['GET', 'POST'])
def weight():
	weights = get_past_week()
	return render_template('weight.html', 
						page_title="Weight Tracking",
						quote=handle_quote_of_day(),
						weights=weights,
						no_weights=len(weights))

@app.route('/weight/add')
def weight_add():
	return render_template('weight-add.html',
							page_title="Add a new Weight Entry",
							quote=handle_quote_of_day())

@app.route('/weight/search', methods=['GET', 'POST'])
def weight_search():
	if request.method == 'GET':
		return render_template('weight-search.html',
								page_title="Weight Search",
								quote=handle_quote_of_day(),
								search=False)
	elif request.method == 'POST':
		return render_template('weight-search.html',
								page_title="Weight Search",
								quote=handle_quote_of_day(),
								search=True,
								tstamp_start=request.form['tstamp_start'],
								tstamp_stop=request.form['tstamp_stop'])

@app.route('/weight/delete')
def weight_delete():
	weights = Weight.query.all()
	return render_template('weight-delete.html',
							page_title="Delete a Weight Entry",
							quote=handle_quote_of_day(),
							weights=weights)

@app.route('/api/weight/delete', methods=['POST'])
def api_weight_delete():
	if request.method == 'POST':
		weight = Weight.query.filter_by(tstamp=request.form['tstamp']).first()
		print(weight)
		db.session.delete(weight)
		db.session.commit()
		return redirect(url_for('weight_delete'))

@app.route('/api/weight/add/weight', methods=['POST'])
def api_add_weight():
	print(request.form.to_dict())
	weight_d = request.form.to_dict()
	weight = Weight(
		weight=float(weight_d['weight']),
		tstamp=weight_d['tstamp']
	)
	db.session.add(weight)
	db.session.commit()
	return redirect(url_for('weight'))


@app.route('/api/weight/plot/<start>/<stop>')
def figure_search_plot(start : str, stop : str):
	fig = Figure(figsize=(9.375, 8))
	ax = fig.add_subplot(1,1,1)
	weights = get_weights_by_time(start, stop)
	xs = []
	ys = []
	for weight in weights:
		xs.append(weight.tstamp)
		ys.append(weight.weight)
	payload = {}
	for i in range(len(xs)):
		# Collect all the data into a dictionary
		payload[xs[i]] = ys[i]
	out_time = sorted(payload.keys(), reverse=False)
	out_val = []
	for t in out_time:
		out_val.append(payload[t])
	print(out_time)
	print(out_val)
	ax.plot(out_time, out_val, '--')
	ax.scatter(out_time, out_val)
	ax.tick_params(axis='x', rotation=45)
	ax.set_title('Time Range from {} to {}'.format(out_time[0], out_time[len(out_time)-1]))
	ax.set_ylabel('Weight [lbs]')
	output = BytesIO()
	FigureCanvas(fig).print_png(output)
	return Response(output.getvalue(), mimetype='image/png')

@app.route('/api/weight/hist/<start>/<stop>')
def figure_search_hist(start : str, stop : str):
	fig = Figure(figsize=(9.375, 8))
	ax = fig.add_subplot(1,1,1)
	weights = get_weights_by_time(start, stop)
	ys = []
	for weight in weights:
		ys.append(weight.weight)
	ax.hist(ys)
	ax.tick_params(axis='x', rotation=45)
	ax.set_title('Time Range from {} to {}'.format(start, stop))
	ax.set_xlabel('Weight [lbs]')
	ax.set_ylabel('Counts()')
	output = BytesIO()
	FigureCanvas(fig).print_png(output)
	return Response(output.getvalue(), mimetype='image/png')

@app.route('/api/week/weight/plot')
def figure_plot():
	fig = Figure(figsize=(9.375, 8))
	ax = fig.add_subplot(1,1,1)
	weights = get_past_week()
	if len(weights) > 0:
		xs = []
		ys = []
		for weight in weights:
			xs.append(weight.tstamp)
			ys.append(weight.weight)
		payload = {}
		for i in range(len(xs)):
		# Collect all the data into a dictionary
			payload[xs[i]] = ys[i]
		out_time = sorted(payload.keys(), reverse=False)
		out_val = []
		for t in out_time:
			out_val.append(payload[t])
		print(out_time)
		print(out_val)
		ax.plot(out_time, out_val, '--')
		ax.scatter(out_time, out_val)
		ax.tick_params(axis='x', rotation=45)
		ax.set_title('Time Range from {} to {}'.format(out_time[0], out_time[len(out_time)-1]))
		ax.set_ylabel('Weight [lbs]')
	output = BytesIO()
	FigureCanvas(fig).print_png(output)
	return Response(output.getvalue(), mimetype='image/png')


@app.route('/food-diary')
def food_diary():
	now = datetime.datetime.now()
	food_diaries = Food_Diary.query.all()
	food_diary = None
	if len(food_diaries) > 0:
		for diary in food_diaries:
			print(diary.tstamp)
			tstamp = datetime.datetime.strptime(diary.tstamp, '%Y-%m-%d')
			if now.day == tstamp.day and now.year == tstamp.year and now.month == tstamp.month:
				food_diary = diary
	return render_template('food-diary.html',
						page_title="Today's Food Diary",
						quote=handle_quote_of_day(),
						food_diary=food_diary,
						have_diary=len(food_diaries))

@app.route('/food-diary/add')
def food_diary_add():
	return render_template('food-diary-add.html',
							page_title="Food Diary Add",
							quote=handle_quote_of_day(),
							update=False,
							food_diary=None)

@app.route('/food-diary/update')
def food_diary_update():
	food_diaries = Food_Diary.query.all()
	return render_template('food-diary-update.html',
							page_title="Update a Food Diary Entry",
							quote=handle_quote_of_day(),
							food_diaries=food_diaries,
							have_diary=len(food_diaries))

@app.route('/food-diary/update/form', methods=['POST'])
def food_diary_update_form():
	return render_template('food-diary-add.html',
							page_title="Update a Food Diary Form",
							quote=handle_quote_of_day(),
							update=True,
							food_diary=request.form.to_dict())

@app.route('/food-diary/delete')
def food_diary_delete():
	food_diaries = Food_Diary.query.all()
	return render_template('food-diary-delete.html',
						page_title="Delte a Food Diary",
						quote=handle_quote_of_day(),
						food_diaries=food_diaries,
						have_diary=len(food_diaries))

@app.route('/api/food-diary/add/food-diary', methods=['POST'])
def api_food_diary_add():
	food_diary = process_food_diary(request.form.to_dict())

	fd = Food_Diary(
		breakfast=food_diary['breakfast'],
		b_cal=float(food_diary['b_cal']),
		lunch=food_diary['lunch'],
		l_cal=float(food_diary['l_cal']),
		dinner=food_diary['dinner'],
		d_cal=float(food_diary['d_cal']),
		snack=food_diary['snack'],
		s_cal=float(food_diary['s_cal']),
		tstamp=food_diary['tstamp']
	)
	db.session.add(fd)
	db.session.commit()
	return redirect(url_for('food_diary'))


@app.route('/api/food-diary/delete', methods=['POST'])
def api_food_diary_delete():
	food_diary = Food_Diary.query.filter_by(tstamp=request.form['tstamp']).first()
	db.session.delete(food_diary)
	db.session.commit()
	return redirect(url_for('food_diary_delete'))


@app.route('/api/food-diary/update', methods=['POST'])
def api_food_diary_update():
	food_diary = process_food_diary(request.form.to_dict())
	db.session.query(Food_Diary). \
			filter(Food_Diary.tstamp == request.form['tstamp']). \
			update({
				'breakfast' : food_diary['breakfast'],
				'b_cal' : food_diary['b_cal'],
				'lunch' : food_diary['lunch'],
				'l_cal' : food_diary['l_cal'],
				'dinner' : food_diary['dinner'],
				'd_cal' : food_diary['d_cal'],
				'snack' : food_diary['snack'],
				's_cal' : food_diary['s_cal']
			})
	db.session.commit()
	return redirect(url_for('food_diary_update'))

def book_convert_tags(book_entry : dict):
	taglist = []
	keys = book_entry.keys()
	tagstr = ''
	for key in keys:
		if 'tag' in key:
			taglist.append(book_entry[key])
	for i in range(len(taglist)):
		if i == len(taglist) - 1:
			tagstr += taglist[i]
		else:
			tagstr += taglist[i] + ', '
	return tagstr

def book_check_for_empty(book : dict):
	book_entry = {
		'title' : book['title'],
		'author' : book['author'],
		'owned' : book['owned'],
		'have_read' : book['have_read'],
		'rating' : book['rating'],
		'is_series' : book['is_series'],
		'no_in_series' : book['no_in_series'],
		'tags' : book['tags']
	}
	for key in book_entry.keys():
		if book_entry[key] == '':
			if key == 'rating' or 'no_in_series':
				book[key] = 0
			elif key == 'owned' or 'have_read' or 'is_series':
				book[key] = 'False'
			else:
				book[key] = 'NONE'
	return book 

@app.route('/bookworm')
def book_home():
	books = Book.query.all()
	return render_template('frontpage.html',
                           page_title='Bookworms-R-Us! 📖',
                           page_description='A library for a little book worm!',
						   no_of_books=len(books),
						   books=books, method='none')

@app.route('/bookworm/add-book')
def add_book():
	return render_template('add-book.html',
						   page_title='Add a New Book! 📖',
                           page_description='Always better to have more books!',
						   method='add')

@app.route('/bookworm/update-book', methods=['POST'])
def update_book():
	return render_template('add-book.html',
						   page_title='Update a Book! 📖',
                           page_description='Make sure that everything is in its place!',
						   method='update',
						   book=request.form.to_dict())

@app.route('/bookworm/search')
def search_book():
	return render_template('add-book.html',
						   page_title='Search for a Book! 📖',
                           page_description='Hope you find something good!',
						   method='search')

@app.route('/bookworm/search-results', methods=['POST'])
def search_results():
	content = request.form.to_dict()
	content['tags'] = book_convert_tags(content)
	tags = content['tags']
	taglist = tags.split(',')
	book_list = []
	books = Book.query.all()
	for book in books:
		print(book)
		found_by_tag = False
		for tag in taglist:
			if tag.lower() in book.tags.lower() and tag != '':
				print("Adding {} to list from {}".format(book, tag))
				book_list.append(book)
				found_by_tag = True
				break
		if book.title.lower() == content['title'].lower() or \
			book.author.lower() == content['author'].lower() or \
				book.owned == content['owned'] or \
					book.have_read == content['have_read'] or \
						book.rating == content['rating'] or \
							book.is_series == content['is_series'] or \
								book.no_in_series == content['no_in_series'] and not found_by_tag:
				book_list.append(book)
				print("Adding {} to list from {}".format(book, content))
				continue
	print(book_list)
	return render_template('frontpage.html',
                           page_title='Bookworms-R-Us! 📖',
                           page_description='Search Results Away!',
						   no_of_books=len(book_list),
						   books=book_list, method='search')

@app.route('/api/update/book', methods=['POST'])
def api_update_book():
	book = request.form.to_dict()
	book['tags'] = book_convert_tags(book)
	book = book_check_for_empty(book)
	db.session.query(Book). \
		filter(Book.title == str(book['title'])). \
			update({
				'title' : book['title'],
				'author' : book['author'],
				'owned' : book['owned'],
				'have_read' : book['have_read'],
				'rating' : book['rating'],
				'is_series' : book['is_series'],
				'no_in_series' : book['no_in_series'],
				'tags' : book['tags']
			})
	db.session.commit()
	return redirect(url_for('book_home'))

@app.route('/api/delete/book', methods=['POST'])
def api_delete_book():
	book = request.form.to_dict()
	book_entry = Book.query.filter_by(title=book['title']).first()
	print(book)
	db.session.delete(book_entry)
	db.session.commit()
	return redirect(url_for('book_home'))

@app.route('/api/add/book', methods=['POST'])
def api_add_book():
	book = request.form.to_dict()
	book['tags'] = book_convert_tags(book)
	book = book_check_for_empty(book)
	print(book)
	book_entry = Book(title=book['title'],
		author=book['author'],
		owned=book['owned'],
		have_read=book['have_read'],
		rating=book['rating'],
		is_series=book['is_series'],
		no_in_series=book['no_in_series'],
		tags=book['tags'])
		
	db.session.add(book_entry)
	db.session.commit()
	return redirect(url_for('book_home'))


def book_to_dict(books : list):
	book_list = []
	for book in books:
		print(book)
		book_list.append({
			'title' : book.title,
			'author' : book.author,
			'owned' : book.owned,
			'have_read' : book.have_read,
			'rating' : book.rating,
			'is_series' : book.is_series,
			'no_in_series' : book.no_in_series,
			'tags' : book.tags 
		})
	return book_list