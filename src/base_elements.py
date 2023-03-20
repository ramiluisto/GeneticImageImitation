from PIL import Image, ImageDraw
import graycode
import random
import math

DEBUG = True
DEFAULT_TEST_IMAGE_FILEPATH = "./data/RamiSquare.png"
BLOCK_COUNT_DEFAULT = 16
DEFAULT_CANVAS_SIZE = (512, 512)
IMAGE_FORMAT = "RGB"


if DEBUG:
    random.seed = 42


class Canvas:
    def __init__(
        self,
        src_image_filepath=DEFAULT_TEST_IMAGE_FILEPATH,
        block_count=BLOCK_COUNT_DEFAULT,
        canvas_size=DEFAULT_CANVAS_SIZE,
        image_format=IMAGE_FORMAT,
    ):

        self.src_image_filepath = src_image_filepath
        self.block_count = block_count
        self.canvas_size = canvas_size
        self.image_format = image_format

        self.blocks = [self._create_random_block() for _ in range(self.block_count)]

    def _create_random_block(self):
        x_max, y_max = self.canvas_size
        random_coords = (
            random.randint(0, x_max),
            random.randint(0, x_max),
            random.randint(0, y_max),
            random.randint(0, y_max),
        )

        random_color_data = (
            random.randint(0, 256),
            random.randint(0, 256),
            random.randint(0, 256),
        )

        random_transparency = random.randint(0, 256)

        block = Block(random_coords, random_color_data, random_transparency)
        return block

    def draw(self, filename=None):
        base = self.create_blank_canvas()

        for block in self.blocks:
            self.draw_block_to_canvas(base, block)

        if filename != None:
            base.save(filename)

        return base

    def create_blank_canvas(self):
        im = Image.new(
            mode=self.image_format, size=self.canvas_size, color=(255, 255, 255)
        )
        return im

    def draw_block_to_canvas(self, base, block):
        drw = ImageDraw.Draw(base, "RGBA")
        x0, x1, y0, y1 = block.coordinates
        rect_coords = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]
        fill = (*block.color, block.transparency)
        drw.polygon(xy=rect_coords, fill=fill)

    def score(self, comparison_image=None):
        if comparison_image == None:
            comparison_image = Image.open(DEFAULT_TEST_IMAGE_FILEPATH)

        current_image = self.draw()

        score = self.image_distance(current_image, comparison_image)

        return score


    def image_distance(self, current_image, comparison_image):

        distances = tuple(
            self.point_distance(curr, comp)
            for curr, comp in zip(current_image.getdata(), comparison_image.getdata())
        )


        return sum(distances)/len(distances)

    def point_distance(self, rgb_1, rgb_2):
        distance = 0
        for a, b in zip(rgb_1, rgb_2):
            distance += abs(b - a) / 256.0

        return distance / 3.0


class Block:
    def __init__(self, location_coords, color_data, transparency):

        x0, x1, y0, y1 = location_coords
        self.coordinates = (x0, x1, y0, y1)

        self.color = tuple(color_data)
        self.transparency = transparency

    @property
    def code(self):
        code_block = ""

        for coord in self.coordinates:
            code_block += self.number_to_code_string(coord)

        for color in self.colors:
            code_block += self.number_to_code_string(color)

        code_block += self.number_to_code_string(self.transparency)

        return code_block

    @staticmethod
    def number_to_code_string(number):
        return "{:09b}".format(graycode.tc_to_gray_code(number))

    @staticmethod
    def code_string_to_number(code_string):
        return graycode.gray_code_to_tc(int(ncode_string, base=2))

    def __hash__(self):
        pass
