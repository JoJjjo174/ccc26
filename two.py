import re

FILE = "level-2/in_level-2_1-small.txt"

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

        if len(line) < 4 and line:
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

sequence_results = []

for s in sequences:
    cost = 0
    inventory = {}

    for recipe in s:
        for input_item in recipe.inputs:
            amount = recipe.inputs[input_item]

            if input_item in inventory:
                inventory[input_item] -= amount

                if inventory[input_item] < 0:
                    buy_amount = abs(inventory[input_item])
                    inventory[input_item] = 0

                else:
                    buy_amount = 0

            else:
                buy_amount = amount

            cost += prices[input_item] * buy_amount

        for output_item in recipe.outputs:
            amount = recipe.outputs[output_item]

            if output_item in inventory:
                inventory[output_item] += amount

            else:
                inventory[output_item] = amount

    sequence_results.append(
        (cost, inventory)
    )

with open("output2.txt", "w") as file:
    for res in sequence_results:
        cost = res[0]
        inv = res[1]

        line = str(cost) + " -> "

        for item in inv:
            if inv[item] == 0:
                continue

            line += str(inv[item]) + " " + item + ", "

        file.write(line[:-2]+"\n")



        

