import random
from time import sleep

import requests
import useragent
from bs4 import BeautifulSoup
# from user_agent import generate_user_agent
import json
import csv
import lxml

orig_url = "https://health-diet.ru/table_calorie/"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0"
}
orig_req = requests.get(orig_url, headers=headers)

orig_src = orig_req.text

with open("index.html", "w") as file:
    file.write(orig_src)

with open("index.html") as file:
    orig_src = file.read()

orig_soup = BeautifulSoup(orig_src, "lxml")





# ПОЛУЧИЛИ ВСЕ КАТЕГОРИИ С ССЫЛКАМИ
all_content_href = orig_soup.find_all(class_="mzr-tc-group-item-href")

all_content_dict = {}
for item in all_content_href:
    item_text = item.text
    item_href = "https://health-diet.ru" + item.get("href")

    all_content_dict[item_text] = item_href

with open("all_content_dict", "w") as file:
    json.dump(all_content_dict, file, indent=4, ensure_ascii=False)





#
with open("all_content_dict") as file:
    all_content = json.load(file)

iteration_count = int(len(all_content)) - 1
count = 0
print(f"Всего итераций: {iteration_count}")

for content_name, content_href in all_content.items():

    rep = [",", " ", "-", "'"]
    for item in rep:
        if item in content_name:
            content_name = content_name.replace(item, "_")
    req = requests.get(url=content_href, headers=headers)
    src = req.text

    with open(f"data/{content_name}_{count}.html", "w") as file:
        file.write(src)

    with open(f"data/{content_name}_{count}.html") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    # ПРОВЕРКА СТРАНИЦЫ НА НААЛИЧИЕ ТАБЛИЦЫ
    alert_block = soup.find(class_="uk-alert")
    if alert_block is not None:
        continue

    # ПОЛУЧАЕМ ЗАГОЛОВКИ ТАБЛИЦЫ
    table_header = soup.find(class_="mzr-tc-group-table").find("tr").find_all("th")
    product = table_header[0].text
    calories = table_header[1].text
    proteins = table_header[2].text
    fats = table_header[3].text
    uglev = table_header[4].text

    with open(f"data/{content_name}_{count}.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                product,
                calories,
                proteins,
                fats,
                uglev
            )
        )
    # ПОЛУЧАЕМ ДАННЫЕ ПРОДУКТОВ
    product_data = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")

    product_info = []
    for item in product_data:
        product_tds = item.find_all("td")

        title = product_tds[0].find("a").text
        calories = product_tds[1].text
        proteins = product_tds[2].text
        fats = product_tds[3].text
        uglev = product_tds[4].text

        product_info.append(
            {
                "Title": title,
                "Calories": calories,
                "Proteins": proteins,
                "Fats": fats,
                "Carbohydrates": uglev
            }
        )

        with open(f"data/{content_name}_{count}.csv", "a", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    title,
                    calories,
                    proteins,
                    fats,
                    uglev
                )
            )

    with open(f"data/{content_name}_{count}.json", "a", encoding="utf-8") as file:
        json.dump(product_info, file, indent=4, ensure_ascii=False)

    count += 1
    print(f"Итерация {count}. {content_name} записан")
    iteration_count = iteration_count - 1

    if iteration_count == 0:
        print('Работа завершена')
        break

    print(f"Осталось итераций: {iteration_count}")
