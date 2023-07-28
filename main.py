from flask import Flask, render_template, request, redirect
from datetime import datetime
from Kitapsepeti import Kitapsepeti
from Alternatifkitap import Alternatifkitap
import sqlite3 as sql
import matplotlib
import os
matplotlib.use("Agg")
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home_page():
    if request.method == "POST":
        book_title = request.form["book_title"]
        return redirect(f"/{book_title}")

    return render_template("index.html")


@app.route('/<book_title>', methods=['GET', 'POST'])
def get_price(book_title):
    if request.method == "POST":
        book_title = request.form["book_title"]
        return redirect(f"/{book_title}")

    book_title = book_title.capitalize()

    kitapsepeti_book = Kitapsepeti(book_title)
    kitapsepeti_book.get_price()

    alternatifkitap_book = Alternatifkitap(book_title)
    alternatifkitap_book.get_price()

    all_results = []

    kitapsepeti_result = {
        "website": kitapsepeti_book.website_name,
        "book_name": kitapsepeti_book.book_title,
        "price": kitapsepeti_book.price,
        "author": kitapsepeti_book.author,
        "publisher": kitapsepeti_book.publisher,
        "book_url": kitapsepeti_book.book_url,
    }

    if kitapsepeti_result["price"] is not None:
        all_results.append(kitapsepeti_result)

    alternatifkitap_result = {
        "website": alternatifkitap_book.website_name,
        "book_name": alternatifkitap_book.book_title,
        "price": alternatifkitap_book.price,
        "author": alternatifkitap_book.author,
        "publisher": alternatifkitap_book.publisher,
        "book_url": alternatifkitap_book.book_url,
    }
    if alternatifkitap_result["price"] is not None:
        all_results.append(alternatifkitap_result)
    sorted_results = []
    sorted_results = sorted(all_results, key=lambda d: d['price'])

    if not sorted_results:
        return render_template("index.html", not_found=True)
    lowest_price_data = sorted_results[0]

    crate_table(book_title)
    insert_or_update_data(book_title, lowest_price_data)
    plot_data(book_title)

    return render_template("price_list.html", all_results=sorted_results)


def crate_table(book_title):
    db = sql.connect("books.db")
    cursor = db.cursor()

    table_name = book_title.capitalize().replace(" ", "_")
    cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            book_name TEXT,
            price REAL,
            date TEXT,
            website TEXT
        )
    """)
    db.commit()
    db.close()


def insert_or_update_data(book_title, lowest_price_data):
    db = sql.connect("books.db")
    cursor = db.cursor()

    table_name = book_title.capitalize().replace(" ", "_")
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Check if data exists for the current date
    cursor.execute(f'SELECT * FROM {table_name} WHERE date = ?', (current_date,))
    existing_data = cursor.fetchone()

    if not existing_data:
        # If there's no data for the current date, insert the lowest price data
        cursor.execute(f'INSERT INTO {table_name} (book_name, price, date, website) VALUES (?, ?, ?, ?)', (
            lowest_price_data["book_name"],
            lowest_price_data["price"],
            current_date,
            lowest_price_data["website"]
        ))
    else:
        # If data exists for the current date, compare prices and update if needed
        if lowest_price_data["price"] < existing_data[2]:
            cursor.execute(f'DELETE FROM {table_name} WHERE date = ?', (current_date,))
            cursor.execute(f'INSERT INTO {table_name} (book_name, price, date, website) VALUES (?, ?, ?, ?)', (
                lowest_price_data["book_name"],
                lowest_price_data["price"],
                current_date,
                lowest_price_data["website"]
            ))
    db.commit()
    db.close()


def plot_data(book_title):
    db = sql.connect("books.db")
    cursor = db.cursor()

    table_name = book_title.capitalize().replace(" ", "_")
    cursor.execute(f""" SELECT price, date FROM {table_name}""")
    data = cursor.fetchall()

    db.close()

    df = pd.DataFrame(data, columns=["price", "date"])
    df["date"] = pd.to_datetime(df["date"])

    chart_path = f"static/charts/{book_title.capitalize()}.png"
    if os.path.exists(chart_path):
        print(chart_path)
        os.remove(chart_path)
    fig = plt.figure(facecolor='#F7FBFC')
    plt.figure(figsize=(6, 4))
    plt.plot(df["date"], df["price"], marker='o', linestyle='-')
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title("Price Analyze")
    plt.xticks(rotation=45)



    plt.savefig(chart_path, dpi= 400,  bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()


if __name__ == '__main__':
    app.run(debug=True)
