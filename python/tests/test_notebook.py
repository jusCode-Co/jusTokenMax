import json

from justokenmax.notebook import notebook_to_markdown


def _nb():
    return json.dumps({
        "cells": [
            {"cell_type": "markdown", "source": ["# Title\n", "some intro"]},
            {"cell_type": "code", "source": ["print('hi')\n", "x = 1"],
             "outputs": [
                 {"output_type": "stream", "text": ["hi\n"]},
                 {"output_type": "display_data",
                  "data": {"image/png": "IMG" + "Q" * 500}},
             ]},
        ],
        "metadata": {}, "nbformat": 4,
    })


def test_keeps_code_and_markdown():
    md, st = notebook_to_markdown(_nb())
    assert st["ok"]
    assert "print('hi')" in md
    assert "# Title" in md


def test_elides_image_output():
    md, st = notebook_to_markdown(_nb())
    assert "[image output elided]" in md
    assert "Q" * 500 not in md
    assert st["images_elided"] == 1


def test_keeps_stream_output():
    md, _ = notebook_to_markdown(_nb())
    assert "hi" in md


def test_non_notebook_passthrough():
    md, st = notebook_to_markdown("not a notebook")
    assert st["ok"] is False
    assert md == "not a notebook"
