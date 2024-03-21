from app.database import (
    create_inventory,
    base_1,
    cursor_1,
    update_ongoing_inventor
)

from app.utils import generate_unique_inv_id
from datetime import datetime

# print(check_ongoing_inventory(cursor_1))
update_ongoing_inventor(base_1, cursor_1, '1111')

