from typing import List, Literal, Union, Tuple

RETRIEVAL_METHOD_TO_RANK = {
    "tensor": "lexical",
    "lexical": "tensor",
    "disjunction": "rrf",
}


def get_modifiers(
    order_by: Literal[
        None,
        "asc_average_rating",
        "desc_average_rating",
        "asc_rating_number",
        "desc_rating_number",
        "asc_price",
        "desc_price",
    ]
) -> List[str]:
    """converts the request order_by parameter to a list of score modifiers

    Args:
        order_by (Literal[ None, "asc_average_rating", "desc_average_rating", "asc_rating_number", "desc_rating_number", "asc_price", "desc_price"]): the order_by parameter from the request

    Returns:
        List[str]: the list of score modifiers
    """
    if order_by is None:
        return None

    order, by = order_by.split("_", 1)

    if order == "asc":
        weight = -0.1
    else:
        weight = 0.1

    return {
        "add_to_score": [{"field_name": by, "weight": weight}],
    }


def parse_body(
    data: dict,
) -> Tuple[
    str,
    Literal["tensor", "lexical", "hybrid"],
    Union[None, List[str]],
    Union[None, dict],
]:
    """parses the request body to extract the query, search type, modifiers and hybrid parameters

    Args:
        data (dict): the request body

    Returns:
        Tuple[str, Literal["tensor", "lexical", "hybrid"], Union[None, List[str]], Union[None, dict]]: the query, search type, modifiers and hybrid parameters
    """
    query = data["query"]
    search_type: Literal["tensor", "lexical", "hybrid"] = data["search_type"]
    retrieval_method: Literal[None, "lexical", "tensor", "disjunction"] = data.get(
        "retrieval_method"
    )

    ranking_method = RETRIEVAL_METHOD_TO_RANK[retrieval_method]

    lexical_searchable_attributes: Union[
        None,
        List[
            Literal[
                "title", "store", "features", "description", "categories", "details"
            ]
        ],
    ] = data.get("lexical_searchable_attributes")

    order_by: Literal[None, "average_rating", "rating_number", "price"] = data.get(
        "order_by"
    )

    modifiers = get_modifiers(order_by)
    print(data["alpha"])
    alpha: float = data.get("alpha", 0.5)

    if alpha > 1:
        alpha = 1
    elif alpha < 0:
        alpha = 0

    searchable_attributes = None
    if search_type != "tensor":
        searchable_attributes = lexical_searchable_attributes

    hybrid_parameters = None
    if search_type == "hybrid":
        hybrid_parameters = {
            "retrievalMethod": retrieval_method,
            "rankingMethod": ranking_method,
            "searchableAttributesLexical": searchable_attributes,
        }
        if ranking_method == "rrf":
            hybrid_parameters["alpha"] = alpha
            hybrid_parameters["rrfK"] = 60

        if modifiers is not None and retrieval_method == "disjunction":
            hybrid_parameters["scoreModifiersTensor"] = modifiers
            hybrid_parameters["scoreModifiersLexical"] = modifiers

    return query, search_type, modifiers, hybrid_parameters
