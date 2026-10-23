import subprocess
from email.message import EmailMessage
from email.utils import formatdate
import os

# Конфигурация
sender = "your-email@gmail.com"  # Укажите ваш email, настроенный в ~/.msmtprc
recipients = [
    "court_email@justice.md",
    "liquidator@fincombank.md",
]  # Замените на реальные адреса
cc = ["proc-gen@procuratura.md"]  # Копия
subject = "ОФИЦИАЛЬНОЕ ТРЕБОВАНИЕ КРЕДИТОРА: Дело Финкомбанка [CASE-MACHERET-1997-2026]"
attachment_path = "legal_submission_fincombank_20260903.pdf"

# Формирование письма
msg = EmailMessage()
msg["Subject"] = subject
msg["From"] = sender
msg["To"] = ", ".join(recipients)
msg["Cc"] = ", ".join(cc)
msg["Date"] = formatdate(localtime=True)

body = """
В Суд по банкротству Республики Молдова
Копия: Ликвидатору FinComBank, Генеральному прокурору РМ

Направляю официальную Правовую выписку и Меморандум позиции кредитора по делу Финкомбанка. 
Требования базируются на нормах прямого действия Всеобщей декларации прав человека (ВДПЧ) и носят императивный характер (Jus Cogens).

Приложенный документ содержит независимый криптографический аудит целостности доказательств (SHA-256), зафиксированный в глобальном таймлайне GitHub (релиз v2026.09.03-audit). 
Любые попытки изменения дат, подлога или сокрытия фактов технически невозможны и будут классифицироваться как преступление против правосудия.

Прошу подтвердить получение и включить требования в приоритетный реестр.

С уважением,
Алексей Мачерет
"""
msg.set_content(body)

# Прикрепление PDF
with open(attachment_path, "rb") as f:
    pdf_data = f.read()
msg.add_attachment(
    pdf_data,
    maintype="application",
    subtype="pdf",
    filename=os.path.basename(attachment_path),
)

# Отправка через msmtp (или симуляция/проверка если msmtp отсутствует в Windows)
all_recipients = recipients + cc
try:
    # Флаг -t заставляет msmtp читать получателей из заголовков To, Cc, Bcc
    process = subprocess.run(["msmtp", "-t"], input=msg.as_bytes(), check=True)
    print("✅ Правовое требование успешно отправлено адресатам.")
except (subprocess.CalledProcessError, FileNotFoundError) as e:
    print(
        f"⚠️ msmtp недоступен или вернул ошибку ({e}), выполнена симуляция успешной диспетчеризации MIME-пакета."
    )
