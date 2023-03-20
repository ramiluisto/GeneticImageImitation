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

    @classmethod
    def canvas_from_code(cls, code_str):
        block_strings = [
            code_str[68*j : 68*(j+1)] for j in range(BLOCK_COUNT_DEFAULT)
        ]


        fresh_canvas = cls()
        fresh_canvas.blocks = [
            Block.block_from_code_string(code_string) for code_string in block_strings
        ]


        return fresh_canvas


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
            random.randint(0, x_max-1),
            random.randint(0, x_max-1),
            random.randint(0, y_max-1),
            random.randint(0, y_max-1),
        )

        random_color_data = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

        random_transparency = random.randint(0, 255)

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

        return sum(distances) / len(distances)

    def point_distance(self, rgb_1, rgb_2):
        distance = 0
        for a, b in zip(rgb_1, rgb_2):
            distance += abs(b - a) / 256.0

        return distance / 3.0


    def canvas_to_code_string(self):
        canvas_code = ""
        for block in self.blocks:
            canvas_code += block.code

        return canvas_code

class Block:
    def __init__(self, location_coords, color_data, transparency):

        location_coords = [max(0, min(value, 511)) for value in location_coords]

        x0, x1, y0, y1 = location_coords
        self.coordinates = (x0, x1, y0, y1)


        self.color = tuple(color_data)
        self.transparency = transparency

    @classmethod
    def block_from_code_string(cls, code_string):
        
        location_coords = [
            cls.code_string_to_number(code_string[9*i:9*(i+1)]) for i in range(0,4)
        ]

        color_data = [
            cls.code_string_to_number(code_string[36+8*i:36+8*(i+1)]) for i in range(0,3)
        ]

        transparency = cls.code_string_to_number(code_string[-8:])

        return cls(location_coords, color_data, transparency)

    @property
    def code(self):
        code_block = ""

        for coord in self.coordinates:
            code_block += self.number_to_code_string(coord, 511)

        for color_val in self.color:
            code_block += self.number_to_code_string(color_val, 255)

        code_block += self.number_to_code_string(self.transparency, 255)

        return code_block

    @staticmethod
    def number_to_code_string(number, max_value):
        padding_count = int(math.ceil(math.log(max_value + 1, 2)))
        format_string = "{:0" + str(padding_count) + "b}"
        code = format_string.format(graycode.tc_to_gray_code(number))

        return code

    @staticmethod
    def code_string_to_number(code_string):
        try:
            num = graycode.gray_code_to_tc(int(code_string, base=2))
        except Exception as e:
            print(code_string)
        return num

    def __hash__(self):
        pass
