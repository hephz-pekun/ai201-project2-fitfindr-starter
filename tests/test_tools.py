# tests/test_tools.py
from tools import (
search_listings,
suggest_outfit,
create_fit_card
)
def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []   # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)

def test_create_fit_card_empty_outfit():
    result = create_fit_card(
        "",
        {"title": "Vintage Tee"}
    )
    assert isinstance(result, str)
    assert "Unable to create" in result

def test_create_fit_card_blank_outfit():

    result = create_fit_card(
        "   ",
        {"title": "Vintage Tee"}
    )

    assert isinstance(result, str)


def test_suggest_outfit_empty_wardrobe():

    wardrobe = {"items": []}

    # Should not crash
    result = suggest_outfit(
        {"title": "Vintage Tee"},
        wardrobe
    )

    assert isinstance(result, str)
    assert len(result) > 0

