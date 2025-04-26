from django.shortcuts import render

DATA = {
    'omlet': {
        'яйца, шт': 2,
        'молоко, л': 0.1,
        'соль, ч.л.': 0.5,
    },
    'pasta': {
        'макароны, г': 0.3,
        'сыр, г': 0.05,
    },
    'buter': {
        'хлеб, ломтик': 1,
        'колбаса, ломтик': 1,
        'сыр, ломтик': 1,
        'помидор, ломтик': 1,
    },
    # можете добавить свои рецепты ;)
}


def recipe_view(request, dish):
    if dish in DATA:
        recipe = DATA[dish].copy()
        servings = request.GET.get('servings')
        if servings:
            try:
                for ingridient in recipe:
                    recipe[ingridient] *= int(servings)
            except ValueError:
                print(f'Число порций должно быть целым числом')
        context = {
            'recipe': recipe
        }
    else:
        context = {
            'recipe': {}
        }
    return render(request, 'calculator/index.html', context)
        