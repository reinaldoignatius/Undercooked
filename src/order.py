class Order:
    def __init__(self, id, name, required_ingredients, allocated_time, maximum_reward):
        self.id = id
        self.name = name
        self.required_ingredients = required_ingredients
        self.remaining_time = allocated_time
        self.allocated_time = allocated_time
        self.maximum_reward = maximum_reward

    def match(self, ingredients):
        if len(self.required_ingredients) != len(ingredients):
            return False
        for required_ingredient in self.required_ingredients:
            ingredient_found = False
            for ingredient in ingredients:
                if ingredient.name == required_ingredient['name']:
                    ingredient_found = True
                    if len(required_ingredient['required_processes']) != len(ingredient.processes_done):
                        return False
                    for required_process in required_ingredient['required_processes']:
                        if not required_process in ingredient.processes_done:
                            return False
                    break
            if not ingredient_found:
                return False
        return True
