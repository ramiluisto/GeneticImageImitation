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


def test_score():
    for j in range(10):
        canvas = base_elements.Canvas()
        score = canvas.score()
        canvas.draw(f"./tests/test_dump/test_{score}.png")


