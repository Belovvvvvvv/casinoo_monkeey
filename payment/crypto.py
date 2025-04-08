import uuid
from aiocryptopay import AioCryptoPay, Networks
from config import CRYPTO_BOT_TOKEN
from utils.logger import logger

class CryptoPayment:
    def __init__(self):
        self.crypto = AioCryptoPay(token=CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)
        self.active_invoices = {}  # Словарь для хранения активных счетов

    async def create_invoice(self, user_id: int, amount: float) -> dict:
        try:
            invoice = await self.crypto.create_invoice(
                asset='USDT',
                amount=amount,
                description=f'Пополнение баланса для пользователя {user_id}'
            )
            # Сохраняем информацию о счете
            self.active_invoices[invoice.invoice_id] = {
                'user_id': user_id,
                'amount': amount
            }
            logger.success(f"Счет успешно создан для пользователя {user_id}: {amount} USDT")
            return {
                "bot_invoice_url": invoice.bot_invoice_url,
                "amount": amount,
                "invoice_id": invoice.invoice_id
            }
        except Exception as e:
            logger.error(f"Ошибка при создании счета для пользователя {user_id}: {str(e)}")
            return None

    async def check_payment(self, invoice_id: str) -> bool:
        try:
            invoice = await self.crypto.get_invoices(invoice_ids=[invoice_id])
            if invoice and invoice[0].status == 'paid':
                # Удаляем счет из активных
                invoice_info = self.active_invoices.pop(invoice_id, None)
                if invoice_info:
                    logger.success(f"Платеж по счету {invoice_id} успешно подтвержден")
                    return True
            return False
        except Exception as e:
            logger.error(f"Ошибка при проверке платежа для счета {invoice_id}: {str(e)}")
            return False

    async def send_payment(self, user_id: int, amount: float):
        try:
            transfer = await self.crypto.transfer(
                user_id=user_id,
                asset='USDT',
                amount=amount,
                spend_id=uuid.uuid4()
            )
            return transfer
        except Exception as e:
            logger.error(f"Ошибка при отправке платежа пользователю {user_id}: {str(e)}")
            return None 
