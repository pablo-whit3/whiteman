import re
import json

with open("raw.txt", "r", encoding="utf8") as file:
    text = file.read()

pattern_products = r"\n(?P<order>[0-9]+)\.\n(?P<name>.+)\n(?P<count>[0-9, ]+)\s*x\s*(?P<price>[0-9 ,]+)\n(?P<sum>[0-9 ,]+)"

products = []

for m in re.finditer(pattern_products, text):
    product = {
        "№": m.group("order"),
        "Название": m.group("name"),
        "Количество": m.group("count").strip(),
        "Цена": m.group("price").strip(),
        "Стоимость": m.group("sum").strip()
    }
    products.append(product)

pattern_datetime = r"Время:\s*(?P<datetime>\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})"
datetime_match = re.search(pattern_datetime, text)

datetime_value = None
if datetime_match:
    datetime_value = datetime_match.group("datetime")

pattern_payment = r"(?P<method>Банковская карта|Наличный расчет):"
payment_match = re.search(pattern_payment, text)

payment_method = None
if payment_match:
    payment_method = payment_match.group("method")

pattern_total = r"ИТОГО:\n(?P<total>[0-9 ]+,\d{2})"
total_match = re.search(pattern_total, text)

total_amount = None
if total_match:
    total_amount = total_match.group("total")

result = {
    "products": products,
    "Дата и время": datetime_value,
    "Способ оплаты": payment_method,
    "Итого": total_amount
}

print(json.dumps(result, ensure_ascii=False, indent=2))