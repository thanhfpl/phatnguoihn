import requests
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Thay YOUR_TOKEN bằng token của bot bạn nhận được từ BotFather
TOKEN = 'YOUR_TOKEN'
API_URL = 'https://vietcheckcar.com/api/api.php?api_key=sfund&bsx={}&bypass_cache=0&loaixe=2&vip=0'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Chào mừng bạn đến với bot của tôi! Gửi /tracuu để tra cứu.')

async def tracuu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        user_message = update.message  # Lưu tin nhắn của người dùng
        user_id = update.message.from_user.id  # Lấy ID người dùng
        query = ' '.join(context.args)  # Biển số xe người dùng nhập
        api_request_url = API_URL.format(query)

        # Gửi tin nhắn thông báo đang xử lý
        processing_message = await update.message.reply_text('Đang xử lý...')
        
        response = requests.get(api_request_url)

        if response.status_code == 200:
            data = response.json()
            total_violations = data.get('totalViolations', 0)

            if total_violations > 0:
                # Có vi phạm, lấy thông tin chi tiết
                violations = data.get('violations', [])
                violation_messages = []
                for violation in violations:
                    violation_messages.append(
                        f"**Trạng thái:** {violation['trang_thai']}\n"
                        f"**Biển kiểm sát:** {violation['bien_kiem_sat']}\n"
                        f"**Thời gian vi phạm:** {violation['thoi_gian_vi_pham']}\n"
                        f"**Địa điểm vi phạm:** {violation['dia_diem_vi_pham']}\n"
                        f"**Hành vi vi phạm:** {violation['hanh_vi_vi_pham']}\n"
                        f"**Đơn vị phát hiện:** {violation['don_vi_phat_hien_vi_pham']}\n"
                        f"**Số điện thoại:** {violation['so_dien_thoai']}\n"
                        f"**Nội giải quyết vụ việc:** {violation['noi_giai_quyet_vu_viec']}\n"
                        f"---"
                    )
                message = '\n'.join(violation_messages)
            else:
                # Không có vi phạm
                current_time = datetime.now().strftime("%H:%M:%S, %d/%m/%Y")
                message = (f"Biển số {query} không có lỗi vi phạm. "
                           f"Mong bạn tiếp tục tuân thủ luật giao thông và lái xe an toàn, "
                           f"dữ liệu được cập nhật vào: {current_time}.")
        else:
            message = 'Có lỗi xảy ra khi truy cập API.'

        # Đợi 3 giây trước khi trả về dữ liệu
        await asyncio.sleep(3)
        
        # Xóa tin nhắn của người dùng
        await user_message.delete()
        # Cập nhật tin nhắn đang xử lý với nội dung kết quả và tag người dùng
        await processing_message.edit_text(f"@{update.message.from_user.username}, {message}", parse_mode='Markdown')
    else:
        await update.message.reply_text('Vui lòng cung cấp biển số xe để tra cứu.')

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("tracuu", tracuu))

    application.run_polling()

if __name__ == '__main__':
    main()
