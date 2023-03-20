import src.base_elements as base_elements
import pytest


@pytest.fixture
def simple_canvas():
    return base_elements.Canvas()


def test_self():
    assert True


def test_canvas_init():
    canvas = base_elements.Canvas()


def test_draw(simple_canvas):

    simple_canvas.draw("./tests/draw_test_image.png")


def test_block_code(simple_canvas):
    for idx, block in enumerate(simple_canvas.blocks):
        code = block.code
        print(f"{idx:>3} : {code}")
        for bit in code:
            assert bit in {"0", "1"}

        print(block.coordinates, block.color, block.transparency)
        assert len(code) == 68, f"Error with code: {code}"


def test_block_from_code_string(simple_canvas):
    block = simple_canvas.blocks[0]

    new_block = block.block_from_code_string(block.code)

    assert new_block.coordinates == block.coordinates
    assert new_block.color == block.color 
    assert new_block.transparency == block.transparency
    assert id(block) != id(new_block)
    new_block.transparency = -1
    assert new_block.transparency != block.transparency


        

def test_score():
    for j in range(10):
        canvas = base_elements.Canvas()
        score = canvas.score()
        canvas.draw(f"./tests/test_dump/test_{score}.png")


def test_canvas_strings():
    canvas = base_elements.Canvas()
    val_1 = canvas.draw()
    canvas_code = canvas.canvas_to_code_string()
    canvas_code = canvas.canvas_to_code_string()
    val_2 = base_elements.Canvas.canvas_from_code(canvas_code).draw()

    assert val_1 == val_2