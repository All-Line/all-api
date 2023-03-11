from utils.choices.language_choices import LANGUAGE_CHOICES


def test_language_choices():
    assert LANGUAGE_CHOICES == (
        ("en", "English"),
        ("fr", "French"),
        ("de", "German"),
        ("it", "Italian"),
        ("ja", "Japanese"),
        ("pt-br", "Portuguese (Brazil)"),
        ("pt-pt", "Portuguese (Portugal)"),
        ("es", "Spanish"),
    )
