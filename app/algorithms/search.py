from typing import Callable, TypeVar

T = TypeVar("T")


def contains_int(values: list[int], target: int) -> bool:
    """Busca linear simples para verificar se um inteiro existe na lista."""
    for value in values:
        if value == target:
            return True
    return False


def contains_text(text: str, term: str) -> bool:
    """
    Verifica manualmente se 'term' aparece dentro de 'text'.

    Usamos busca linear caractere a caractere porque o projeto proíbe
    atalhos nativos de busca como `in` e `find()` para esse tipo de operação.
    """
    normalized_text = text.lower()
    normalized_term = term.lower().strip()

    if normalized_term == "":
        return True

    text_length = len(normalized_text)
    term_length = len(normalized_term)

    if term_length > text_length:
        return False

    start_index = 0
    while start_index <= text_length - term_length:
        term_found = True
        offset = 0

        while offset < term_length:
            if normalized_text[start_index + offset] != normalized_term[offset]:
                term_found = False
                break
            offset += 1

        if term_found:
            return True

        start_index += 1

    return False


def filter_by_predicate(items: list[T], predicate: Callable[[T], bool]) -> list[T]:
    """
    Filtra uma lista manualmente com busca linear.

    A lista é pequena neste projeto acadêmico, então a busca linear é suficiente
    e mantém o código simples de entender.
    """
    filtered_items: list[T] = []
    for item in items:
        if predicate(item):
            filtered_items.append(item)
    return filtered_items
