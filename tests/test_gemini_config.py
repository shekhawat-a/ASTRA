from api import GEMINI_MODEL


def test_gemini_model_is_flash_3_1():
    assert GEMINI_MODEL == "gemini-3.1-flash"
