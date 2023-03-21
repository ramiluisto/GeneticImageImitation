import src_numpy.base_elements as base_elements
import pytest


@pytest.fixture
def simple_block():
    coords = [10, 20, 100, 105]
    rgba = [255, 255, 255, 255]
    block = base_elements.Block(coords, rgba)
    return block


@pytest.fixture
def nonstandard_block():
    coords = [0, 2, 5, 8]
    rgba = [2, 19, 29, 39]
    block = base_elements.Block(
        coords, rgba, canvas_size=(10, 10), rgba_dimensions=(10, 20, 30, 40)
    )
    return block


def test_self():
    assert True


def test_Block_init():
    coords = [10, 20, 100, 105]
    rgba = [255, 255, 255, 255]
    block = base_elements.Block(coords, rgba)

    assert block.x_coord_bit_width == 9
    assert block.y_coord_bit_width == 9
    assert block.rgba_bit_widths == (8, 8, 8, 8)

    coords = [-10, 20, 5000, 105]
    rgba = [1000, 255, 255, 255]
    block = base_elements.Block(coords, rgba)

    for coord in block.coordinates:
        assert coord <= 511
        assert coord >= 0

    for val in block.rgba:
        assert val <= 255
        assert val >= 0

    coords = [-10, 20, 5000, 105]
    rgba = [1000, 255, 255, 255]
    block = base_elements.Block(
        coords, rgba, canvas_size=(10, 10), rgba_dimensions=(10, 20, 30, 40)
    )
    for coord in block.coordinates:
        assert coord <= 10
        assert coord >= 0

    assert block.rgba == (9, 19, 29, 39)

    assert block.x_coord_bit_width == 4
    assert block.y_coord_bit_width == 4
    assert block.rgba_bit_widths == (4, 5, 5, 6)


def test_code_beneration(simple_block, nonstandard_block):
    assert len(simple_block.code) == simple_block.code_width
    assert len(nonstandard_block.code) == nonstandard_block.code_width

    assert simple_block.code != nonstandard_block.code
    assert len(simple_block.code) == 68


def test_bit_width_from_dim(simple_block):
    assert simple_block.get_bit_width_from_dimension(512) == 9
    assert simple_block.get_bit_width_from_dimension(513) == 10
    assert simple_block.get_bit_width_from_dimension(-4) == 0


def test_graycodes(simple_block):
    for width in range(0, 5):
        for j in range(2, 10):
            code = simple_block.number_to_code_string(j, width)
            num = simple_block.code_string_to_number(code)

            assert num == j


def test_block_gen_from_string(simple_block, nonstandard_block):
    canvas = base_elements.Canvas()
    block_conf = {
        "canvas_size": canvas.canvas_size,
        "rgba_dimensions": canvas.rgba_dimensions,
    }

    code = canvas.blocks[0].code
    print(code)
    new_block = base_elements.Block.from_code_string(
        code,
        code_configuration=canvas.block_code_configuration,
        block_configuration=block_conf,
    )

    assert code == new_block.code
    assert canvas.blocks[0].coordinates == new_block.coordinates
    assert canvas.blocks[0].rgba == new_block.rgba


def test_canvas_init():
    canvas = base_elements.Canvas()
    canvas.code
    canvas.__hash__


def test_canvas_code_init():
    canvas = base_elements.Canvas()
    code = canvas.code

    canvas_configuration = {
        "src_image_filepath": canvas.src_image_filepath,
        "block_count": canvas.block_count,
        "canvas_size": canvas.canvas_size,
        "image_format": canvas.image_format,
        "rgba_dimensions": canvas.rgba_dimensions,
    }
    new_canvas = base_elements.Canvas.from_code_string(
        code,
        canvas_code_configuration=canvas.canvas_code_configurations,
        canvas_configuration=canvas_configuration,
    )


def test_mutate():
    for j in range(10):
        canvas = base_elements.Canvas()
        old_code = canvas.code
        canvas.mutate(j)
        assert sum(a != b for a, b in zip(old_code, canvas.code)) == j


def test_mate():
    canvas_1 = base_elements.Canvas()
    canvas_2 = base_elements.Canvas()

    child = canvas_1.mate(canvas_2)

    child.code
