
FILE = "in_level-1_0-example.txt"

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
            for i in ingredients:
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






