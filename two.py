import re

FILE = "level-2/in_level-2_0-example.txt"

class Recipe():
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs

prices = {}

sequences = []

with open(FILE, "r") as input:
    lines = [line.rstrip() for line in input.readlines()]
    line_i = 1
    for line in lines[line_i:]:
        line_i += 1
        line = line
        if not line or line == "\n":
            break

        price, molecule = line.split(" -> ")
        prices[molecule] = int(price)

    line_i += 2

    current_sequence = []
    for line in lines[line_i:]:
        line_i += 1

        if len(line) == 1:
            sequences.append(current_sequence)
            current_sequence = []

        elif not line or line == "\n":
            continue

        else:
            recipe_split = line.split(" -> ")
            ingredients = recipe_split[0].split(", ")
            result = recipe_split[1].split(", ")
            
            ingredient_molecules = {}
            for i in ingredients:
                amount, name = i.split()
                amount = int(amount)
                ingredient_molecules[name] = amount
            
            output_molecules = {}
            for i in result:
                amount, name = i.split()
                amount = int(amount)
                output_molecules[name] = amount
            
            recipe = Recipe(ingredient_molecules, output_molecules)
            
            current_sequence.append(recipe)

    sequences.append(current_sequence)

for s in sequences:
    print(s)

        

