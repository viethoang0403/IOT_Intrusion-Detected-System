import telegram

API_TOKEN = '7308293337:AAFS9jjCzE5hoQecagFP3DUTKZtxXgjg52Q'
CHAT_ID = '6733536444'
bot = telegram.Bot(token=API_TOKEN)

async def send_telegram(photo_path="alert.png"):
    try:
        # Gửi tin nhắn cảnh báo
        await bot.send_message(chat_id=CHAT_ID, text="Cảnh báo: Có xâm nhập, nguy hiểm!")
        # Gửi ảnh cảnh báo
        with open(photo_path, 'rb') as image_file:
            await bot.send_photo(chat_id=CHAT_ID, photo=image_file)
        print("Gửi thành công!")
    except Exception as ex:
        print(f"Không thể gửi tin nhắn Telegram: {ex}")
