__DBNAME__ = None

def initDB(name):
    global __DBNAME__  # add this line!
    if __DBNAME__ is None: # see notes below; explicit test for None
        __DBNAME__ = name
    else:
        raise RuntimeError("Database name has already been set.")

