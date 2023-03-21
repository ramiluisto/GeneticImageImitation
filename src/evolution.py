from src.base_elements import Canvas
import random
from icecream import ic
from pprint import pprint

CANVAS_COUNT = 16


class Simulation:
    def __init__(self, iter_threshold = 10):
        self.canvases = [Canvas()  for _ in range(CANVAS_COUNT)]
        self.scored_canvases = {canvas : canvas.score() for canvas in self.canvases}
        self.iter_threshold = iter_threshold

    def run(self):  
        self.iter_count = 0

        while self.continue_evolving():
            print(f"Running round {self.iter_count:>4}...")
            self.do_one_round()

    def continue_evolving(self):
        return self.iter_count <= self.iter_threshold

    def do_one_round(self):
        self.sort_canvases_by_score()
        self.drop_worst()
        self.mate_best()
        self.mutate()
        self.scored_canvases = {canvas : canvas.score() for canvas in self.canvases}
        self.iter_count += 1
        

    def sort_canvases_by_score(self):
        self.canvases = sorted(self.canvases, 
                               key=lambda x: self.scored_canvases[x])
        

    def drop_worst(self):
        self.canvases = self.canvases[:-4]

    def mate_best(self):
        CHILD_COUNT = 4
        
        best_a, best_b = self.canvases[0:2]
        code_a = best_a.code
        code_b = best_b.code
        
        children = []
        for _ in range(CHILD_COUNT):
            new_child = ""

            for j in range(len(code_a)//68):
                block_a = code_a[68*j : 68*(j+1)]
                block_b = code_b[68*j : 68*(j+1)]

                if random.choice([True, False]):
                    new_child += block_a
                else:
                    new_child += block_b
            child = Canvas.canvas_from_code(new_child)
            children.append(child)

        self.canvases = children + self.canvases

    def mutate(self):
        new_canvases = []
        for idx, canvas in enumerate(self.canvases):
            mutation_count = max(idx, 8)
            code = canvas.code
            code = self.mutate_code(code, mutation_count)
            canvas = canvas.canvas_from_code(code)
            new_canvases.append(canvas)

        self.canvases = new_canvases


    def mutate_code(self, code, count):

        new_code = ""
        indeces = random.sample(range(len(code)), count)
        for idx, bit in enumerate(code):
            if not (idx in indeces):
                new_bit = bit
            else:
                new_bit = "0" if bit == "1" else "1"

            new_code += new_bit

        return new_code

    def best_image(self, filepath=None):
        return self.canvases[0].draw()

