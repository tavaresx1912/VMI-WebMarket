from datetime import datetime
from typing import TypeVar

T = TypeVar("T")


def insertion_sort_by_datetime_desc(items: list[T], attribute_name: str) -> list[T]:
    """
    Ordena manualmente objetos por um atributo datetime em ordem decrescente.

    Usamos insertion sort porque as listagens de pedidos deste projeto tendem a ser
    pequenas e o algoritmo é simples o bastante para fins didáticos.
    """
    sorted_items = list(items)

    index = 1
    while index < len(sorted_items):
        current_item = sorted_items[index]
        current_value: datetime = getattr(current_item, attribute_name)
        previous_index = index - 1

        while previous_index >= 0:
            previous_value: datetime = getattr(sorted_items[previous_index], attribute_name)
            if previous_value >= current_value:
                break

            sorted_items[previous_index + 1] = sorted_items[previous_index]
            previous_index -= 1

        sorted_items[previous_index + 1] = current_item
        index += 1

    return sorted_items
