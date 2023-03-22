from PIL import Image
import numpy as np
from src_numpy.base_elements import Canvas

DEFAULT_TEST_IMAGE_FILEPATH = "./data/RamiSquare.png"
CANVAS_COUNT = 16


class Simulation:
    @staticmethod
    def load_image_as_np_array(filepath):
        comparison_image = Image.open(filepath).convert("RGB")

        return np.array(comparison_image)

    def __init__(
        self,
        comparison_image_filepath=DEFAULT_TEST_IMAGE_FILEPATH,
        iter_limit=5,
        canvas_count=CANVAS_COUNT,
        canvas_init_data={},
    ):
        self.comp_img = self.load_image_as_np_array(comparison_image_filepath)
        self.canvases = [Canvas(**canvas_init_data) for _ in range(CANVAS_COUNT)]
        self.scored_canvases = {
            canvas: canvas.score(self.comp_img) for canvas in self.canvases
        }
        self.iter_limit = iter_limit
        self.best_results = []

    def run(self, iter_idx=0):
        while iter_idx <= self.iter_limit:
            print(f"\rDoing round {iter_idx:>6}.     ", end="")
            self.do_one_round()
            iter_idx += 1
        print("\n")

    def do_one_round(self):
        self.sort_canvases_by_score()
        self.drop_worst()
        self.mate_best()
        self.mutate()
        self.scored_canvases = {
            canvas: canvas.score(self.comp_img) for canvas in self.canvases
        }

    def sort_canvases_by_score(self):
        self.canvases = sorted(self.canvases, key=lambda x: self.scored_canvases[x])
        best = self.canvases[0]
        self.best_results.append((best, self.scored_canvases[best]))

    def drop_worst(self):
        self.canvases = self.canvases[:-4]

    def mate_best(self):
        CHILD_COUNT = 2
        best_a, best_b = self.canvases[0:2]
        children = []
        for _ in range(CHILD_COUNT):
            child = best_a.mate(best_b)
            children.append(child)

        third_best = self.canvases[2]
        child = best_a.mate(third_best)
        children.append(child)
        child = best_b.mate(third_best)
        children.append(child)

        self.canvases = self.canvases + children

    def mutate(self):
        for idx, canvas in enumerate(self.canvases):
            canvas.mutate(idx)

    def best_image(self, filepath=None):
        return self.canvases[0].draw()
