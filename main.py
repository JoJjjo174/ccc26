
FILE = "in_level-1_2-large.txt"

class Molecule():
    def __init__(self, amount, mol):
        self.amount = amount
        self.mol = mol

class Recipe():
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs

class Collection():
    def __init__(self, materials, recipe):
        self.materials = materials
        self.recipe = recipe

collections = []

with open(FILE, "r") as input:
    current_collection = Collection([], None)

    for line in input.readlines()[1:]:

        if not line or line == "\n":
            collections.append(current_collection)
            current_collection = Collection([], None)

        elif "->" in line:
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

            current_collection.recipe = recipe

        else:
            split_line = line.rstrip().split(", ")

            available_molecules = {}
            for i in split_line:
                amount, name = i.split()
                amount = int(amount)
                available_molecules[name] = amount

            current_collection.materials = available_molecules


for collection in collections:
    for ingredient in collection.recipe.inputs:
        collection.materials[ingredient] -= collection.recipe.inputs[ingredient]

    for output in collection.recipe.outputs:
        if output not in collection.materials:
            collection.materials[output] = collection.recipe.outputs[output]
        else:
            collection.materials[output] += collection.recipe.outputs[output]

with open("output1.txt", "w") as output_file:
    for collection in collections:
        coll_string = ""
        for molecule in collection.materials:
            if collection.materials[molecule] != 0:
                coll_string += str(collection.materials[molecule]) + " " + str(molecule) + ", "


        output_file.write(coll_string[:-2]+"\n")






