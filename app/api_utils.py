from app.models import Recipe, Quote
import datetime
import requests
from app import db

def to_dict(recipe : Recipe):
    ingredients = recipe.ingredients
    ingredients_list = ingredients.split(',')
    recipe_dict = {
        'recipe_name' : recipe.recipe_name,
        'servings' : recipe.servings,
        'prep_time' : recipe.prep_time,
        'cook_time' : recipe.cook_time,
        'ingredients' : ingredients_list,
        'directions' : recipe.directions,
        'notes' : recipe.notes
    }
    return recipe_dict

def directions_to_list(dir_str : str):
    dir_list = dir_str.split(',')
    return dir_list


def search_recipe(search_args : dict):
    recipes = Recipe.query.all()
    recipe_list = []
    search_ingredients = []
    if search_args['ingredients'] != '':
        search_ingredients = search_args['ingredients'].split(',')
    for recipe in recipes:
        recipe_d = to_dict(recipe)
        recipe_d['directions'] = directions_to_list(recipe_d['directions'])
        ingredient_found = False
        for ingredient in search_ingredients:
            if ingredient.lower() in recipe_d['ingredients'].lower():
                recipe_list.append(recipe_d)
                ingredient_found = True
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
        now = datetime.datetime.now()
        tstamp = datetime.datetime.strptime(last_quote.fetched_on, '%Y-%m-%d %H:%M:%S.%f')
        dt = now - tstamp
        if dt >= datetime.timedelta(days=1):
            new_quote = get_random_quote()
            '''
            db.session.update({
                'author' : new_quote['author'],
                'quote' : new_quote['quote'],
                'fetched_on' : str(datetime.datetime.now())
            })
            '''
            db.session.query(Quote). \
			filter(Quote.id == 1). \
			update({
				'author' : new_quote['author'],
				'quote' : new_quote['quote'],
				'fetched_on' : str(datetime.datetime.now())
			})

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