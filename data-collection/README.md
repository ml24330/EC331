## Data collection

This directory contains files relevant to collecting eBay auction data. The strategy was as follows:

- The titles of tablets listings from selected police accounts are collected;
- Using these titles, similar listings from other sellers on eBay are identified;
- Attributes of each listing are collected by both automatic and manual means.

Due to the timely nature of eBay auctions, it is not possible to replicate exact datasets. Nonetheless, the following steps do outline the process of collecting new data in the same fashion:

1. Delete ```listings.db```, ```matchedauctions.txt```, and ```policeauctions.txt```.
2. Load a suitably configured Python environment with ```selenium``` and ```sqlite3``` installed.
3. Run ```db_init.py```. This creates a fresh ```listings.db``` database.
4. Run ```policelistings.py```. This navigates to the listing pages of electronic tablets of police auctioneers from Sussex and Leicester, and scrapes all titles of listings before storing them inside ```policeauctions.txt```.
5. Run ```search.py```. This takes all titles collected in step 4 and uses them to search on eBay for similar listings, where the IDs of these listings are stored in ```matchedauctions.txt```.
6. Run ```scrape.py```. This iterates through every ID collected in step 5, and scrapes automatically some attributes of the listing, including condition, shipping time, postage, end time, and the seller's name. A row populated with these information is then created for each listing and inserted to ```listings.db```.
7. Run ```update.py```. This iterates through every listing in the database that was inserted in step 6, and opens an interactive window requiring user input to manually collect the attributes of brand, model, screen size, storage, RAM, resolution, quantity, and return policy. The database is then updated with these information.
8. Finally, run ```seller.py```. This scrapes seller-specific information pertaining to their feedback scores, number of feedbacks received, and feedback ratings over the past twelve months. Using a dictionary, these information are inserted to each listing inside the database.
9. Done! If you query the ```listings``` table inside ```listings.db```, there should be approximately 400 similar listings waiting to be analysed.
