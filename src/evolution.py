from scr.base_elements import Canvas



CANVAS_COUNT = 8

class Simulation:


    def __init__(self):
        self.canvases = [Canvas() for _ in range(CANVAS_COUNT)]
        self.iter_threshold = 100
        


    def run(self):
        self.iter_count = 0
        
        while self.continue_evolving():
            self.do_one_round()


    def continue_evolving(self):


        return self.iter_count < self.iter_threshold


    def do_one_round(self):
        self.sort_canvases_by_score()
        self.mate_best()
        self.drop_worst()
        self.mutate()
        self.iter_count += 1 



    def best_image(self, filepath = None):
        pass

