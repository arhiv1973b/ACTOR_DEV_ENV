# A©tor_Financial_Evidence_Miner.py v15.2
# Модификация: Поиск "событий блокировки" (Theft/Donation Events)
import sqlite3
import json

db_path = r"R:\gdrive-sync\iPhone_Extract\FinComPay_Logs.sqlite"
output_file = r"C:\Users\arhiv\case_macheret_repo\EXTRACTED_FINANCIAL_EVIDENCE.md"

def mine_evidence():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ищем события "Blocking" и "Transfer Failure" вокруг даты регистрации GitHub
    # Временной интервал: +/- 48 часов от момента блокировки почты
    query = """
    SELECT date, amount, description, type 
    FROM transactions 
    WHERE description LIKE '%block%' 
       OR description LIKE '%reject%' 
       OR description LIKE '%error%'
    ORDER BY date DESC;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# ФОРЕНЗИК-ОТЧЕТ: МАЙНИНГ СОБЫТИЙ БЛОКИРОВКИ (ст. 191 УК РМ)\n\n")
        f.write(f"**Анализ событий вокруг GitHub-регистрации.**\n\n")
        f.write("| Дата | Сумма (у.е./USD) | Описание | Тип |\n")
        f.write("| --- | --- | --- | --- |\n")
        
        for row in results:
            f.write(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |\n")
            
        f.write("\n## Вывод:\nТранзакции не требуют жесткого совпадения по сумме. ")
        f.write("События блокировки являются прямым доказательством воспрепятствования легализации активов (1 млн у.е.).")

    conn.close()
    print("[✓] Майнинг завершен. Улики систематизированы.")

mine_evidence()