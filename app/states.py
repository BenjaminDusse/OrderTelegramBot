from aiogram.dispatcher.filters.state import State, StatesGroup


class InventoryState(StatesGroup):
    handle_file_data = State()
    waiting_for_barcode = State()
    waiting_for_count = State()
    options = State()
    inventory_close_decision = State()
    inventory_completed = State()
