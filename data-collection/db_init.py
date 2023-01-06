import sqlite3

conn = sqlite3.connect("listings.db")

c = conn.cursor()

try:
    c.execute(f"""
        CREATE TABLE listings (
        id integer,
        url text,
        location text,
        brand text,
        model text,
        screenSize integer,
        storage integer,
        postage integer,
        shippingType text,
        endTime text,
        returnsAccepted integer,
        returnsDays integer,
        condition text,
        sellerFeedbackScore integer,
        sellerPositivePercent real,
        sellerName text,
        price real,
        bids text,
        ram text,
        resolution text,
        sellerPositive integer,
        sellerNegative integer,
        quantity integer,
        sellerItemsSold integer,
        UNIQUE(id)
    )""")

    print(f'created table named listings')

    conn.commit()

except Exception as e: 
    print(f'error, {e}')

conn.close()

