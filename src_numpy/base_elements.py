import numpy as np
from PIL import Image, ImageDraw
import graycode
import random
import math

DEFAULT_TEST_IMAGE_FILEPATH = "./data/RamiSquare.png"
BLOCK_COUNT_DEFAULT = 16
DEFAULT_CANVAS_SIZE = (512, 512)  # NOTE THAT INDECES RUN FROM 0..DIM-1
IMAGE_FORMAT = "RGBA"
RBGA_DIMENSIONS = (256, 256, 256, 256)  # NOTE THAT INDECES RUN FROM 0..DIM-1


class Canvas:
    @classmethod
    def from_code_string(cls, code_string, canvas_code_configuration, canvas_configuration):
        new_canvas = cls(**canvas_configuration)

        block_strings = []
        block_count = canvas_code_configuration['block_count']
        block_width = canvas_code_configuration['block_width']
        for block_idx in range(block_count):
            substring = code_string[block_idx*block_width : (block_idx+1)*block_width]
            
            block_strings.append(substring)

        blocks = [
            Block.from_code_string(
                block_string,
                code_configuration=new_canvas.block_code_configuration,
                block_configuration=new_canvas.block_configuration,
            )
            for block_string in block_strings
        ]
        new_canvas.blocks = blocks

        return new_canvas

    def __init__(
        self,
        src_image_filepath=DEFAULT_TEST_IMAGE_FILEPATH,
        block_count=BLOCK_COUNT_DEFAULT,
        canvas_size=DEFAULT_CANVAS_SIZE,
        image_format=IMAGE_FORMAT,
        rgba_dimensions=RBGA_DIMENSIONS,
    ):
        self.src_image_filepath = src_image_filepath
        self.comparison_image_array = self.load_image_as_np_array(src_image_filepath)

        self.block_count = block_count
        self.canvas_size = canvas_size
        self.rgba_dimensions = rgba_dimensions
        self.image_format = image_format

        self.block_configuration = {
            "canvas_size": self.canvas_size,
            "rgba_dimensions": self.rgba_dimensions,
        }
        self.blocks = [self._create_random_block() for _ in range(self.block_count)]

        self.block_code_configuration = self._generate_block_code_configurations()
        self.canvas_code_configurations = self._generate_canvas_code_configurations()

    @staticmethod
    def load_image_as_np_array(filepath):
        comparison_image = Image.open(filepath).convert('RGB')

        return np.array(comparison_image)

    def _generate_block_code_configurations(self):
        block_lengths = {len(block.code) for block in self.blocks}
        assert len(block_lengths) == 1, "Corrupted block structure!"

        block_code_configuration = {
            "total_length": list(block_lengths)[0],
            "coordinates": {
                "x0": self.blocks[0].x_coord_bit_width,
                "x1": self.blocks[0].x_coord_bit_width,
                "y0": self.blocks[0].y_coord_bit_width,
                "y1": self.blocks[0].y_coord_bit_width,
            },
            "rgba": {
                "r": self.blocks[0].rgba_bit_widths[0],
                "g": self.blocks[0].rgba_bit_widths[1],
                "b": self.blocks[0].rgba_bit_widths[2],
                "a": self.blocks[0].rgba_bit_widths[3],
            },
        }
        return block_code_configuration

    def _generate_canvas_code_configurations(self):
        canvas_code_configurations = {
            "block_count": self.block_count,
            "block_width": self.block_code_configuration["total_length"],
        }
        return canvas_code_configurations

    def _create_random_block(self):
        x_max, y_max = self.canvas_size
        y_min, x_min = 0, 0

        random_coords = (
            random.randint(0, x_max - 1),
            random.randint(0, x_max - 1),
            random.randint(0, y_max - 1),
            random.randint(0, y_max - 1),
        )

        random_rgba = tuple(random.randint(0, dim - 1) for dim in self.rgba_dimensions)

        new_block = Block(random_coords, random_rgba, **self.block_configuration)

        return new_block

    def np_array_reprensentation(self):
        base = self.create_blank_canvas()

        for block in self.blocks:
            self.draw_block_to_canvas(base, block)

        self.pil_img = base # for debug

        return np.array(base)

    def create_blank_canvas(self):
        im = Image.new(
            mode="RGB", size=self.canvas_size, color=(255, 255, 255)
        )
        return im

    def draw_block_to_canvas(self, base, block):
        drw = ImageDraw.Draw(base, "RGBA")
        x0, x1, y0, y1 = block.coordinates
        rect_coords = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]
        drw.polygon(xy=rect_coords, fill=block.rgba)



    # Simulation api

    def score(self) -> float:
        np_img = self.np_array_reprensentation().astype(float)
        comp_img = self.comparison_image_array.astype(float)
        return np.linalg(np_img-comp_img)

    def mate(self, other_canvas):
        pass

    def mutate(self, entropy: int, style: str):
        pass

    # Special methods

    @property
    def code(self):
        canvas_code = ""
        for block in self.blocks:
            canvas_code += block.code

        return canvas_code

    def __hash__(self):
        return self.code.__hash__()


class Block:
    @classmethod
    def from_code_string(cls, code_string, code_configuration, block_configuration):
        current_index = 0

        coordinates = []
        coordinate_widths = code_configuration["coordinates"]
        for name, width in coordinate_widths.items():
            subcode = code_string[current_index : current_index + width]
            coord = cls.code_string_to_number(subcode)
            coordinates.append(coord)
            current_index += width

        rgbas = []
        rgba_widths = code_configuration["rgba"]
        for name, width in rgba_widths.items():
            subcode = code_string[current_index : current_index + width]
            value = cls.code_string_to_number(subcode)
            rgbas.append(value)
            current_index += width

        return cls(coordinates, rgbas, **block_configuration)

    def __init__(
        self,
        coordinates: tuple,  # [x0, x1, y0, y1]
        rgba: tuple,  # [r, g, b, a]
        canvas_size=DEFAULT_CANVAS_SIZE,
        rgba_dimensions=RBGA_DIMENSIONS,
    ):
        self.coordinates = coordinates
        self.rgba = rgba
        self.canvas_size = canvas_size
        self.rgba_dimensions = rgba_dimensions

        self.clean_coordinates()
        self.clean_rgba()

        self.calculate_and_set_code_bit_widths()

    def clean_coordinates(self):
        x0, x1, y0, y1 = self.coordinates
        x_dim, y_dim = self.canvas_size

        x0 = self.project_to_interval(x0, 0, x_dim - 1)
        x1 = self.project_to_interval(x1, 0, x_dim - 1)
        y0 = self.project_to_interval(y0, 0, y_dim - 1)
        y1 = self.project_to_interval(y1, 0, y_dim - 1)

        self.coordinates = (x0, x1, y0, y1)

    def clean_rgba(self):
        rgba = []
        for num, upper_limit in zip(self.rgba, self.rgba_dimensions):
            rgba.append(self.project_to_interval(num, 0, upper_limit - 1))

        self.rgba = tuple(rgba)

    @staticmethod
    def project_to_interval(number, lower, upper):
        return min(upper, max(lower, number))

    def calculate_and_set_code_bit_widths(self):
        self.x_coord_bit_width = self.get_bit_width_from_dimension(self.canvas_size[0])
        self.y_coord_bit_width = self.get_bit_width_from_dimension(self.canvas_size[1])
        self.rgba_bit_widths = tuple(
            self.get_bit_width_from_dimension(max_value)
            for max_value in self.rgba_dimensions
        )

        total_width = (
            2 * self.x_coord_bit_width
            + 2 * self.y_coord_bit_width
            + sum(self.rgba_bit_widths)
        )
        self.code_width = total_width

    @staticmethod
    def get_bit_width_from_dimension(max_value: int) -> int:
        if max_value <= 0:
            return 0

        return int(math.ceil(math.log(max_value, 2)))

    @property
    def code(self) -> str:
        coordinate_code = self.generate_coordinate_string()
        rgba_code = self.generate_rgba_string()
        return coordinate_code + rgba_code

    def generate_coordinate_string(self):
        x0, x1, y0, y1 = self.coordinates

        x0_string = self.number_to_code_string(x0, self.x_coord_bit_width)
        x1_string = self.number_to_code_string(x1, self.x_coord_bit_width)
        y0_string = self.number_to_code_string(y0, self.y_coord_bit_width)
        y1_string = self.number_to_code_string(y1, self.y_coord_bit_width)

        result = x0_string + x1_string + y0_string + y1_string
        return result

    def generate_rgba_string(self):
        rgba_substrings = []

        for value, width in zip(self.rgba, self.rgba_bit_widths):
            substring = self.number_to_code_string(value, width)
            rgba_substrings.append(substring)

        result = "".join(rgba_substrings)
        return result

    @staticmethod
    def number_to_code_string(number, bit_width):
        format_string = "{bin_code:0{width}b}"  # zero left-pad up to width
        code = format_string.format(
            bin_code=graycode.tc_to_gray_code(number), width=bit_width
        )

        return code

    @staticmethod
    def code_string_to_number(code_string):
        num = graycode.gray_code_to_tc(int(code_string, base=2))
        return num
