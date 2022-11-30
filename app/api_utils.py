from app.models import Food_Diary, Recipe, Quote, Project, Weight, Book
import datetime
import requests
from app import db

def to_dict(recipe : Recipe):
    ingredients = recipe.ingredients
    ingredients_list = ingredients.split(',')
    directions = recipe.directions
    directions_list = directions.split(',')
    recipe_dict = {
        'recipe_name' : recipe.recipe_name,
        'servings' : recipe.servings,
        'prep_time' : recipe.prep_time,
        'cook_time' : recipe.cook_time,
        'ingredients' : ingredients_list,
        'directions' : directions_list,
        'notes' : recipe.notes
    }
    return recipe_dict

def proj_to_dict(project : Project):
    project_d = {
        'name' : project.name,
        'desc' : project.desc,
        'est_comp' : project.est_comp
    }
    return project_d

def process_all_recipes(recipe_list : list):
    out_list = []
    for recipe in recipe_list:
        out_list.append(to_dict(recipe))
    return out_list

def process_all_projects(project_list : list):
    out_list = []
    for project in project_list:
        out_list.append(proj_to_dict(project))
    return out_list

def process_all_weights(weight_list : list):
    out_list = []
    for weight in weight_list:
        out_list.append(
            {'tstamp' : weight.tstamp,
            'weight' : weight.weight}
        )
    return out_list

def process_all_diaries(food_diaries : list):
    out_list = []
    for food_diary in food_diaries:
        out_list.append({
            'breakfast' : food_diary.breakfast,
		    'b_cal' : food_diary.b_cal,
		    'lunch' : food_diary.lunch,
		    'l_cal' : food_diary.l_cal,
		    'dinner' : food_diary.dinner,
		    'd_cal' : food_diary.d_cal,
		    'snack' : food_diary.snack,
		    's_cal' : food_diary.s_cal,
		    'tstamp' : food_diary.tstamp})
    return out_list

def directions_to_list(dir_str : str):
    dir_list = dir_str.split(',')
    return dir_list


def search_recipe(search_args : dict):
    recipes = Recipe.query.all()
    recipe_list = []
    search_ingredients = []
    if search_args['ingredients'] != '':
        if ',' in search_args['ingredients']:
            search_ingredients = search_args['ingredients'].split(',')
        else:
            search_ingredients = [search_args['ingredients']]
    for recipe in recipes:
        recipe_d = to_dict(recipe)
        ingredient_found = False
        for ingredient in search_ingredients:
            for recipe_ing in recipe_d['ingredients']:
                print("Comparing: {}, to: {}".format(ingredient, recipe_ing))
                if ingredient.lower() in recipe_ing.lower():
                    recipe_list.append(recipe_d)
                    ingredient_found = True
                    break
        if not ingredient_found:
            if search_args['servings'] == '' and search_args['prep_time'] == '' and search_args['cook_time'] == '' and search_args['ingredients'] == '':
                recipe_list.append(recipe_d)
            elif search_args['servings'] != '' and search_args['servings'] == recipe_d['servings']:
                recipe_list.append(recipe_d)
            elif search_args['prep_time'] != '' and search_args['prep_time'].lower() == recipe_d['prep_time'].lower():
                recipe_list.append(recipe_d)
            elif search_args['cook_time'] != '' and search_args['cook_time'].lower() == recipe_d['cook_time'].lower():
                recipe_list.append(recipe_d)
            else:
                print("Could not find any matches for: {}".format(search_args))
    return recipe_list


def get_random_quote():
    quote = { 'quote' : 'Could not find a quote :/',
              'author' : ''
            }
    try:
    ## making the get request
        response = requests.get("https://quote-garden.herokuapp.com/api/v3/quotes/random")
        if response.status_code == 200:
            ## extracting the core data
            json_data = response.json()
            data = json_data['data']
            ## getting the quote from the data
            quote['quote'] = data[0]['quoteText']
            quote['author'] = data[0]['quoteAuthor']
            return quote
        else:
            return quote
    except:
        return quote

def handle_quote_of_day():
    quotes = Quote.query.all()
    if len(quotes) > 0:
        last_quote = quotes[len(quotes) - 1]
        author = last_quote.author
        now = datetime.datetime.now()
        tstamp = datetime.datetime.strptime(last_quote.fetched_on, '%Y-%m-%d %H:%M:%S.%f')
        dt = now - tstamp
        print("TSTAMP={}".format(tstamp))
        print("TIME DELTA={}".format(dt))
        print("GT A DAY={}".format(dt >= datetime.timedelta(days=1)))
        if dt >= datetime.timedelta(days=1):
            new_quote = get_random_quote()
            db.session.query(Quote). \
			filter(Quote.author == author). \
			update({
				'author' : new_quote['author'],
				'quote' : new_quote['quote'],
				'fetched_on' : str(datetime.datetime.now())
			})
            db.session.commit()
            return new_quote
        else:
            return {
                'author' : last_quote.author,
                'quote' : last_quote.quote,
                'fetched_on' : last_quote.fetched_on
            }
    else:
        new_quote = get_random_quote()
        quote = Quote(author=new_quote['author'],
                        quote=new_quote['quote'],
                        fetched_on=str(datetime.datetime.now()))
        db.session.add(quote)
        db.session.commit()
        return new_quote

def flatten_list(form_list : list):
    out_str = ''
    for i in range(len(form_list)):
        if i != len(form_list) - 1:
            out_str += form_list[i]+', '
        else:
            out_str += form_list[i]
    return out_str

def process_recipe_form(recipe_d : dict):
    keys = recipe_d.keys()
    ingredient_list, direction_list = [], []
    for key in keys:
        split_arg = key.split('_')
        if split_arg[0] == 'ingredient':
            ingredient_list.append(recipe_d[key])
        elif split_arg[0] == 'directions':
            direction_list.append(recipe_d[key])

    ingredient_list = flatten_list(ingredient_list)
    direction_list = flatten_list(direction_list)
    print(ingredient_list)
    print(direction_list)
    return {
        'ingredients' : ingredient_list,
        'directions' : direction_list
    }


def bulk_upload_to_database(db_data : dict):
    print(50*'/')
    for table in db_data.keys():
        if table == 'projects':
            for project in db_data[table]:
                print("PROJECT")
                print(project)
                is_in = Project.query.filter_by(name=project['name']).first()
                if type(is_in) != Project:
                    p = Project(name=project['name'],
                    desc=project['desc'],
                    est_comp=project['est_comp'])
                    print("Found new project: {}, updating now!".format(p.name))
                    db.session.add(p)
                    db.session.commit()
            
        elif table == 'recipes':
            for recipe in db_data[table]:
                print("RECIPE")
                print(recipe)
                recipe['ingredients'] = flatten_list(recipe['ingredients'])
                is_in = Recipe.query.filter_by(recipe_name=recipe['recipe_name']).first()
                print(type(is_in)) 
                if type(is_in) != Recipe:
                    r = Recipe(recipe_name=recipe['recipe_name'],
                    servings=recipe['servings'],
                    prep_time=recipe['servings'],
                    cook_time=recipe['cook_time'],
                    ingredients=recipe['ingredients'],
                    directions=flatten_list(recipe['directions']),
                    notes=recipe['notes'])
                    print("Found new recipe: {}, updating now!".format(r.recipe_name))
                    db.session.add(r)
                    db.session.commit()
        elif table == 'weights':
            for weight in db_data[table]:
                print("WEIGHT")
                is_in = Weight.query.filter_by(tstamp=weight['tstamp']).first()
                print(type(is_in))
                if type(is_in) != Weight:
                    w = Weight(weight=weight['weight'],
                                tstamp=weight['tstamp'])
                    print("Found new weight: {}, {}. Updating now!".format(w.tstamp, w.weight))
                    db.session.add(w)
                    db.session.commit()
        elif table == 'food_diary':
            for food_diary in db_data[table]:
                is_in = Food_Diary.query.filter_by(tstamp=food_diary['tstamp']).first()
                print(type(is_in))
                if type(is_in) != Food_Diary:
                    fd = Food_Diary(
                        breakfast=food_diary['breakfast'],
		                b_cal=float(food_diary['b_cal']),
		                lunch=food_diary['lunch'],
		                l_cal=float(food_diary['l_cal']),
		                dinner=food_diary['dinner'],
		                d_cal=float(food_diary['d_cal']),
		                snack=food_diary['snack'],
		                s_cal=float(food_diary['s_cal']),
		                tstamp=food_diary['tstamp'])
                    db.session.add(fd)
                    db.session.commit()
        
        elif table == 'books':
            for book in db_data[table]:
                print(book)
                is_in = Book.query.filter_by(title=book['title']).first()
                if type(is_in) != Book:
                    b = Book(
                    title=book['title'],
					author=book['author'],
					owned=book['owned'],
					have_read=book['have_read'],
					rating=book['rating'],
					is_series=book['is_series'],
					no_in_series=book['no_in_series'],
					tags=book['tags']
                    )
                    print("Found new book: {}, updating now!".format(b.title))
                    db.session.add(b)
                    db.session.commit()
    pass

def get_past_week():
    now = datetime.datetime.now()
    week_ago = now - datetime.timedelta(days=7)
    weight_week = []
    weights = Weight.query.all()
    for weight in weights:
        time_weight = datetime.datetime.strptime(weight.tstamp, '%Y-%m-%d')
        if time_weight >= week_ago and time_weight <= now:
            weight_week.append(weight)
    return weight_week

def get_weights_by_time(start_time : str, stop_time : str):
    start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
    stop_time = datetime.datetime.strptime(stop_time, '%Y-%m-%d')
    weights = Weight.query.all()
    weight_list = []
    for weight in weights:
        time_weight = datetime.datetime.strptime(weight.tstamp, '%Y-%m-%d')
        if time_weight >= start_time and time_weight <= stop_time:
            weight_list.append(weight)
    return weight_list


def process_food_diary(food_diary : dict):
    if food_diary['b_cal'] == "":
        food_diary['b_cal'] = 0
    if food_diary['l_cal'] == "":
        food_diary['l_cal'] = 0
    if food_diary['d_cal'] == "":
        food_diary['d_cal'] = 0
    if food_diary['s_cal'] == "":
        food_diary['s_cal'] = 0
    if food_diary['breakfast'] == "":
        food_diary['breakfast'] = "< Not Entered Yet >"
    if food_diary['lunch'] == "":
        food_diary['lunch'] = "< Not Entered Yet >"
    if food_diary['dinner'] == "":
        food_diary['dinner'] = "< Not Entered Yet >"
    if food_diary['dinner'] == "":
        food_diary['dinner'] = "< Not Entered Yet >" 
    return food_diary