from typing import Optional

from ninja import Schema


class PaginationDTO(Schema):
    """
    This is an example of pagination DTO for checking with tests. You should have this class in your project
    named and adjusted to your needs, and import it to testing tools.
    """

    current_page: Optional[int] = None
    total_pages: Optional[int] = None
    total_items: int = None
    has_next: bool = False
    has_previous: bool = False
