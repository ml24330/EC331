import sqlite3

# Query every row and every column
def QueryAll():
    conn = sqlite3.connect("listings.db")
    c = conn.cursor()

    c.execute("SELECT * FROM listings")
    res = c.fetchall()

    conn.close()

    return res


def QueryEmpty():
    conn = sqlite3.connect("listings.db")
    c = conn.cursor()

    c.execute("SELECT * FROM listings WHERE bids is null or bids = ''")
    res = c.fetchall()

    conn.close()

    return res


# Send a specific query
def Query(exp):
    conn = sqlite3.connect("listings.db")
    c = conn.cursor()

    c.execute(exp)
    res = c.fetchall()

    conn.close()

    return res

# Insert several listings
def InsertListings(keys, listings):
    conn = sqlite3.connect("listings.db")
    c = conn.cursor()

    c.executemany(f'INSERT OR IGNORE INTO listings({keys}) VALUES({("?, "*len(listings[0]))[:-2]})', listings)

    conn.commit()
    conn.close()

# Clear one row
def ClearOne(id):
    conn = sqlite3.connect("listings.db")
    c = conn.cursor()

    c.execute(f'DELETE FROM listings WHERE id={id}')

    conn.commit()
    conn.close()

# Update a row
def UpdateItem(id, dict):
    conn = sqlite3.connect("listings.db")
    c = conn.cursor()

    query = ""
    for key in dict.keys():
        query += f'{key}=?, '

    data = tuple(list(dict.values()) + [id])

    c.execute(f"""
        UPDATE listings
        SET {query[:-2]}
        WHERE
            id=?
    """, (data))

    conn.commit()
    print(f'Updated item with ID {id}')

    conn.close()