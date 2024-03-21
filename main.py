import logging
from aiogram import types, executor
from aiogram.dispatcher import FSMContext
from app import utils
# from app.utils import *
from app import keyboards as kb
from app import const
from app import database as db
from app.config import bot, dp

from app.states import *
from app.database import *

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


@dp.message_handler(commands=["start", "restart"], state="*")
async def send_welcome(message: types.Message):
    user = db.get_user(base_1, cursor_1, message)
    if not user:
        db.create_user(base_1, cursor_1, message)
    await utils.check_for_inventory(cursor_1, message)


# @dp.message_handler(state=InventoryState.handle_file_data, content_types=types.ContentTypes.DOCUMENT)
# async def process_file(message: types.Message):
#     if message.document.mime_type == 'text/plain' and message.document.file_name.endswith('.txt'):
#         file_path = os.path.join(os.getcwd(), message.document.file_name)
#         inv_id = inventory_session["inv_id"]

#         # Download the file
#         await message.document.download(destination=file_path)
#         await message.answer('⏰Yuklanmoqda...')
#         print(file_path)

#         # time.sleep(10)

#         db.update_start('inventory.db', file_path)
#         db.create_inventory(base_1, cursor_1, inv_id)
#         inventory_session["active"] = True
#         inventory_session["db_filled"] = True
#         await message.answer(f"Inventarizatsiya yaratildi. {inv_id}", reply_markup=kb.get_main_menu_keyboard())
#         await InventoryState.options.set()
#     else:
#         await message.answer("Iltimos, zag faylini yuklang", reply_markup=kb.remove_kb())


@dp.message_handler(state=InventoryState.handle_file_data, content_types=types.ContentTypes.DOCUMENT)
async def process_file(message: types.Message):
    await message.answer('⏰Yuklanmoqda...')

    destination = os.path.join(os.getcwd(), message.document.file_name)
    await message.document.download(destination=destination)

    db.update_start(db_name_1, destination)

    inv_id = db.get_ongoing_inventory(cursor_1)
    await message.answer(f"Inventarizatsiya yaratildi {inv_id}", reply_markup=kb.get_main_menu_keyboard())
    await InventoryState.options.set()


@dp.message_handler(state=InventoryState.waiting_for_barcode)
async def handle_barcode(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    inv_id = db.get_ongoing_inventory(cursor_1)

    barcode_input = message.text
    if message.text.lower() == "/opt":
        await show_options(message)
        return
    if not barcode_input.isdigit() or barcode_input.isalpha():
        await message.reply("Iltimos, raqam kiriting!")
        return
    else:
        # print(barcode_input, type(barcode_input))
        product = db.fetch_product_by_barcode(base_1, cursor_1, barcode_input)
        document = db.fetch_document(base_1, cursor_1, user_id, inv_id, barcode_input)

        if product:
            if document:
                document_title, document_amount = document
                sent_message = await message.answer(
                    f"Produkt: {document_title}\nBoshlang'ich miqdori: {document_amount}",
                    reply_markup=kb.get_product_amount_btns())
                await InventoryState.waiting_for_count.set()
                await state.update_data(
                    {"current_input": "", "message_id": sent_message.message_id, "barcode_input": barcode_input})
            else:
                product_title, product_amount = product
                sent_message = await message.answer(
                    f"Produkt: {product_title}\nBoshlang'ich miqdori: {product_amount}",
                    reply_markup=kb.get_product_amount_btns())
                await InventoryState.waiting_for_count.set()
                await state.update_data(
                    {"current_input": "", "message_id": sent_message.message_id, "barcode_input": barcode_input})
        else:
            await message.reply("Produkt topilmadi❗\nIltimos qaytadan urinib ko'ring")


@dp.message_handler(state=InventoryState.waiting_for_count)
async def handle_count(message: types.Message, state: FSMContext):
    try:
        count_control_message = "Fakt miqdor: \t"
        await message.delete()

        user_id = message.from_user.id
        user_data = await state.get_data()
        inv_id = db.get_ongoing_inventory(cursor_1)
        amount_msg = message.text

        current_state_data = await state.get_data()
        current_input = current_state_data.get("current_input", "")
        product_code = current_state_data.pop('barcode_input')
        message_id = current_state_data.get("message_id")

        await state.set_data(user_data)

        if amount_msg.lower() == "/opt":
            await show_options(message)
            return

        product = db.fetch_product(base_1, cursor_1, product_code)
        document = db.fetch_document(base_1, cursor_1, user_id, inv_id, product_code)

        if product is None:
            await message.reply("Produkt topilmadi❗\nIltimos, qaytadan urinib ko'ring")
            return

        else:
            if amount_msg == 'Backspace':
                current_input = current_input[:-1] if current_input else ''
            elif amount_msg == 'C':
                current_input = ''
            elif amount_msg == '-':
                if not current_input.startswith('-'):
                    current_input = '-' + current_input
            elif amount_msg == '.':
                if '.' not in current_input:
                    current_input += '.'
            elif amount_msg.isdigit() or amount_msg in ['-', '.']:
                current_input += amount_msg
            elif message.text in [str(i) for i in list(kb.count_buttons)]:
                current_input += amount_msg
            else:
                await message.answer("Gazini berdiku ")

            # if message.text == 'Backspace':
            #     current_input = current_input[:-1]
            # if message.text == 'C':
            #     current_input = ''
            # elif message.text in [str(i) for i in list(kb.count_buttons)]:
            #     current_input += amount_msg

            await state.update_data(current_input=current_input)

            if message_id:
                try:
                    if 'BackSpace' in count_control_message:
                        count_control_message.replace('BackSpace', '')
                    await bot.edit_message_text(chat_id=message.chat.id, message_id=message_id,
                                                text=count_control_message + current_input,
                                                reply_markup=message.reply_markup)
                except Exception as e:
                    print(e)
                    sent_message = await message.answer(count_control_message + current_input,
                                                        reply_markup=message.reply_markup)
                    await state.update_data(message_id=sent_message.message_id)

            amount_msg = current_input
            int_amount = amount_msg[:-2]
            if message.text == 'OK':
                print(int_amount, type(int_amount), float(int_amount))

                int_amount = float(int_amount)
                if document:
                    db.update_document_amount(base_1, cursor_1, user_id, inv_id, product_code, int_amount)
                else:
                    item_id, item_code, title, price, amount, product_barcode = product

                    current_input = current_input[:-2]

                    db.create_document_for_product(base_1, cursor_1, inv_id, item_id, user_id, product_barcode,
                                                   product_code, int_amount)

                    await bot.edit_message_text(chat_id=message.chat.id, message_id=message_id,
                                                text=count_control_message + current_input[:-2],
                                                reply_markup=message.reply_markup)
                product_message = "✅Qabul qilindi!"
                await message.answer(product_message, reply_markup=kb.remove_kb())
                await InventoryState.waiting_for_barcode.set()
    except Exception as e:
        await message.answer(str(e))


@dp.message_handler(lambda message: message.text == const.NEW_INVENTORY, state=InventoryState.options)
async def create_new_inventory(message: types.Message):
    try:
        await InventoryState.waiting_for_barcode.set()
        await message.reply("Produkt shtrix kodini kiriting❗", reply_markup=kb.remove_kb())
    except Exception as e:
        await message.answer(str(e))


# Handler for current inventory report


@dp.message_handler(lambda message: message.text == const.CURRENT_INVENTORY_REPORT, state=InventoryState.options)
async def current_inventory_report(message: types.Message):
    print("In current inventory report")
    inv_id = db.get_ongoing_inventory(cursor_1)
    await db.fetch_document_for_inventory_report(base_1, cursor_1, message, inv_id)


# Handler for updating the database


@dp.message_handler(state=InventoryState.inventory_close_decision)
async def inventory_close_decision_handler(message: types.Message, state: FSMContext):
    try:
        inv_id = db.get_ongoing_inventory(cursor_1)
        if message.text == const.COMPLETE:
            data = await db.fetch_inventory_data(cursor_1, inv_id)

            if not os.path.exists('inv_folder'):
                os.mkdir('inv_folder')

            file_name = f"inv_folder/inventory_{inv_id}.xlsx"
            await db.generate_excel_file(data, file_name)

            with open(file_name, "rb") as file:
                await message.reply_document(file, caption="Bugungi inventarizatsiyada kiritilgan mahsulotlar ro'yxati")

            # Reset the session to allow starting fresh

            await state.reset_state(with_data=True)
            update_ongoing_inventory(base_1, cursor_1, inv_id)

            await message.reply(
                "Inventarizatsiya yakunlandi✔\nQaytadan inventarizatsiyani boshlash uchun /start tugmasini bosing",
                reply_markup=kb.remove_kb())

        if message.text == const.CANCEL:
            await message.answer('Main menu', reply_markup=kb.get_main_menu_keyboard())
            await InventoryState.options.set()
    except Exception as e:
        await message.answer(str(e))


@dp.message_handler(commands=["opt"], state="*")
async def show_options(message: types.Message):
    try:
        await InventoryState.options.set()
        await message.answer("Asosiy menyu:", reply_markup=kb.get_main_menu_keyboard())
    except Exception as e:
        await message.answer(str(e))


@dp.message_handler(state=InventoryState.options)
async def options_handler(message: types.Message):
    try:
        if message.text == const.NEW_INVENTORY:
            await message.reply("Produkt shtrix kodini kiriting❗", reply_markup=kb.remove_kb())
            await InventoryState.waiting_for_barcode.set()
        elif message.text == const.CURRENT_INVENTORY_REPORT:
            await message.reply(const.CURRENT_INVENTORY_REPORT)
            await InventoryState.waiting_for_barcode.set()
            await current_inventory_report(message)
        elif message.text == const.COMPLETE_INVENTORY:
            await message.answer(const.COMPLETE_ASK, reply_markup=kb.get_buttons(const.COMPLETE_INV_BTNS, n=1))
            await InventoryState.inventory_close_decision.set()
        else:
            await message.answer("Asosiy menyu: ")
    except Exception as e:
        await message.answer(str(e))


if __name__ == "__main__":
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
        except Exception as ex:
            print(ex)
