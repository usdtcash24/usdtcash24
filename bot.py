import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

BOT_TOKEN = "8721843596:AAFqQoGvBG-Bks_aCW-vbcFZHPLvhBHNkik"
ADMIN_CHAT_ID = "8202893335"
WEBAPP_URL = "https://usdtcash24.github.io/usdtcash24/"

WALLETS = {
    "USDT_TRC20": "TCfVviUoDhhfJKQCa53PuGteMJ39oKfpVh",
    "USDT_ERC20": "0xF6528026B568AC3d994d357fadC2562d1f9b7D7a",
    "USDT_BSC": "0xF6528026B568AC3d994d357fadC2562d1f9b7D7a",
    "BTC": "bc1q...укажите_биткоин_адрес",
}

RATES = {"USDT": 92.50, "BTC": 6100000}
CASH_THRESHOLD_RUB = 462500  # $5,000

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class ExchangeFSM(StatesGroup):
  choosing_currency = State()
  entering_amount = State()
  choosing_city = State()
  entering_contact = State()
  entering_card = State()


def main_kb():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="📱 Открыть USDT Cash24 (Web-приложение)",
                  web_app=WebAppInfo(url=WEBAPP_URL),
              )
          ],
          [
              InlineKeyboardButton(
                  text="⚡ Быстрый обмен в чате",
                  callback_data="start_chat_exchange",
              )
          ],
          [
              InlineKeyboardButton(
                  text="💬 Поддержка / Оператор",
                  url="https://t.me/ваш_юзернейм",
              )
          ],
      ]
  )


def currencies_kb():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="USDT (TRC-20)", callback_data="cur_USDT_TRC20"
              ),
              InlineKeyboardButton(
                  text="USDT (BEP-20)", callback_data="cur_USDT_BSC"
              ),
          ],
          [
              InlineKeyboardButton(
                  text="USDT (ERC-20)", callback_data="cur_USDT_ERC20"
              ),
              InlineKeyboardButton(
                  text="Bitcoin (BTC)", callback_data="cur_BTC"
              ),
          ],
      ]
  )


def cities_kb():
  cities = [
      "Москва (Сити)",
      "Санкт-Петербург",
      "Казань",
      "Екатеринбург",
      "Новосибирск",
      "Нижний Новгород",
      "Краснодар",
      "Ростов-на-Дону",
  ]
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text=c, callback_data=f"city_{c}")
              for c in cities[i : i + 2]
          ]
          for i in range(0, len(cities), 2)
      ]
  )


@dp.message(CommandStart())
async def start_handler(message: types.Message):
  await message.answer(
      f"Здравствуйте, {message.from_user.first_name}!\n\n"
      "Добро пожаловать в **USDT Cash24**:\n"
      "💳 **До $5,000** — моментальный перевод на карту / СБП РФ\n"
      "💼 **От $5,000** — охраняемые кассы в Москва-Сити и городах РФ (наличные"
      " рубли)\n\n"
      f"📊 Базовые курсы:\n• USDT = `{RATES['USDT']} RUB`\n• BTC ="
      f" `{RATES['BTC']:,} RUB`\n\n"
      "Выберите вариант работы:",
      reply_markup=main_kb(),
      parse_mode="Markdown",
  )


@dp.callback_query(F.data == "start_chat_exchange")
async def choose_currency(callback: types.CallbackQuery, state: FSMContext):
  await callback.message.answer(
      "Выберите криптовалюту для обмена:", reply_markup=currencies_kb()
  )
  await state.set_state(ExchangeFSM.choosing_currency)
  await callback.answer()


@dp.callback_query(
    F.data.startswith("cur_"), ExchangeFSM.choosing_currency
)
async def process_cur(callback: types.CallbackQuery, state: FSMContext):
  cur_key = callback.data.replace("cur_", "")
  await state.update_data(currency=cur_key)
  hint = "0.05" if cur_key == "BTC" else "500"
  await callback.message.answer(
      f"Введите сумму к отправке (например: `{hint}`):", parse_mode="Markdown"
  )
  await state.set_state(ExchangeFSM.entering_amount)
  await callback.answer()


@dp.message(ExchangeFSM.entering_amount)
async def process_amount(message: types.Message, state: FSMContext):
  data = await state.get_data()
  cur_key = data["currency"]
  is_btc = cur_key == "BTC"
  rate = RATES["BTC"] if is_btc else RATES["USDT"]

  try:
    amount = float(message.text.replace(",", ".").strip())
    if amount <= 0:
      raise ValueError
  except ValueError:
    await message.answer("Пожалуйста, введите корректное число.")
    return

  total_rub = int(amount * rate)
  await state.update_data(amount=amount, total_rub=total_rub)

  if total_rub >= CASH_THRESHOLD_RUB:
    await message.answer(
        f"💰 К получению: **{total_rub:,} ₽**\n\n"
        "🛡️ *Сумма превышает $5,000: выплата производится строго НАЛИЧНЫМИ в"
        " кассе (защита от 115-ФЗ).*\n\n"
        "Выберите город получения наличных:",
        reply_markup=cities_kb(),
        parse_mode="Markdown",
    )
    await state.set_state(ExchangeFSM.choosing_city)
  else:
    await message.answer(
        f"💳 К получению: **{total_rub:,} ₽** на карту/СБП\n\n"
        "Введите реквизиты для выплаты (Банк + Номер карты или Телефон СБП):",
        parse_mode="Markdown",
    )
    await state.set_state(ExchangeFSM.entering_card)


@dp.callback_query(F.data.startswith("city_"), ExchangeFSM.choosing_city)
async def process_city(callback: types.CallbackQuery, state: FSMContext):
  city = callback.data.replace("city_", "")
  await state.update_data(city=city)
  await callback.message.answer(
      f"📍 Выбран город: **{city}**\n\n"
      "Укажите ваш контакт (@username или телефон) для выписки пропуска:",
      parse_mode="Markdown",
  )
  await state.set_state(ExchangeFSM.entering_contact)
  await callback.answer()


@dp.message(ExchangeFSM.entering_contact)
async def finish_cash_order(message: types.Message, state: FSMContext):
  data = await state.get_data()
  cur_key = data["currency"]
  wallet = WALLETS.get(cur_key, WALLETS["USDT_TRC20"])
  order_id = f"CASH24-{message.from_user.id % 10000}"
  cash_code = f"VIP-{message.message_id * 19 % 1000}-MSK"

  await message.answer(
      f"✅ **Ордер {order_id} сформирован!**\n\n"
      f"💵 К отправке: `{data['amount']} {cur_key.replace('_', ' ')}`\n"
      f"💰 К получению: **{data['total_rub']:,} ₽ Наличными**\n"
      f"🏢 Локация: **{data['city']}**\n"
      f"🔑 Код бронирования кассы: `{cash_code}`\n\n"
      f"📥 **Адрес кошелька для оплаты:**\n`{wallet}`\n\n"
      "После перевода средств менеджер свяжется с вами для согласования времени визита.",
      parse_mode="Markdown",
  )

  admin_msg = (
      f"🔥 <b>USDT Cash24 | НАЛИЧНЫЕ (VIP)</b>\n\n"
      f"🆔 Ордер: <code>{order_id}</code>\n"
      f"💵 Сумма: {data['amount']} {cur_key}\n"
      f"💰 К выдаче: {data['total_rub']:,} RUB\n"
      f"📍 Город: {data['city']}\n"
      f"🔑 Код кассы: <code>{cash_code}</code>\n"
      f"👤 Клиент: @{message.from_user.username or 'нет'} (Контакт:"
      f" {message.text})"
  )
  await bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode="HTML")
  await state.clear()


@dp.message(ExchangeFSM.entering_card)
async def finish_card_order(message: types.Message, state: FSMContext):
  data = await state.get_data()
  cur_key = data["currency"]
  wallet = WALLETS.get(cur_key, WALLETS["USDT_TRC20"])
  order_id = f"CARD24-{message.from_user.id % 10000}"

  await message.answer(
      f"✅ **Заявка {order_id} сформирована!**\n\n"
      f"💵 К отправке: `{data['amount']} {cur_key.replace('_', ' ')}`\n"
      f"💰 К выплате: **{data['total_rub']:,} ₽**\n"
      f"💳 Реквизиты: `{message.text}`\n\n"
      f"📥 **Адрес кошелька для перевода:**\n`{wallet}`\n\n"
      "Средства поступят на карту в течение 5–15 минут после зачисления.",
      parse_mode="Markdown",
  )

  admin_msg = (
      f"💳 <b>USDT Cash24 | КАРТА / СБП</b>\n\n"
      f"🆔 Ордер: <code>{order_id}</code>\n"
      f"💵 Сумма: {data['amount']} {cur_key}\n"
      f"💰 К выплате: {data['total_rub']:,} RUB\n"
      f"📱 Реквизиты: <code>{message.text}</code>\n"
      f"👤 Клиент: @{message.from_user.username or 'нет'} (ID:"
      f" {message.from_user.id})"
  )
  await bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode="HTML")
  await state.clear()


async def main():
  print("Бот USDT Cash24 запущен...")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
