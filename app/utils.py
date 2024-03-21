import random
from app.database import *
from app.states import *
from app import keyboards as kb


def generate_unique_inv_id():
    """Generates a unique inventory ID that is an integer with 4 digits."""
    seed_value = int(time.time() * 1000)  # Using current time as a seed component
    random.seed(seed_value)
    # Ensures inv_id is between 1000 and 9999
    inv_id = random.randint(1000, 9999)

    return inv_id


async def check_for_inventory(cursor, message):
    current_inventory_id = get_ongoing_inventory(cursor)
    generated_num = generate_unique_inv_id()
    if current_inventory_id:
        await message.reply("Inventarizatsiya raqami: {}".format(current_inventory_id),
                            reply_markup=kb.get_main_menu_keyboard())
        await InventoryState.options.set()
    else:
        create_inventory(base_1, cursor_1, generated_num)
        await message.answer('Iltimos, zag faylini yuklang', reply_markup=kb.remove_kb())
        await InventoryState.handle_file_data.set()

# def delete_db_files():
#     current_folder_path = os.getcwd()
#     for filename in os.listdir(current_folder_path):
#         if filename.endswith('.db'):
#             os.remove(filename)


# def generate_unique_database_name():
#     now = datetime.now()
#     formatted_time = now.strftime("%d%m%Y%H%M%S")
#     database = "inventory_db_{}.db".format(formatted_time)
#     return database
