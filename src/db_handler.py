import sqlite3
import numpy as np
import json
import io

# allows to store np array in sql
def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("array", convert_array)


def create_db():
    conn = sqlite3.connect('static/db/calibration.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()

    c.execute("""CREATE TABLE calibrations (
            src INTEGER,
            h array,
            exposure INTEGER
            )
            """)

    conn.commit()
    conn.close()

def delete_db():
    conn = sqlite3.connect('static/db/calibration.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("DROP TABLE calibrations")
    conn.commit()
    conn.close()

def write_row(src, h, exp):
    conn = sqlite3.connect('static/db/calibration.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("SELECT 1 FROM calibrations WHERE src = {}".format(src))
    response = c.fetchone()

    if response is not None:
        c.execute("UPDATE calibrations SET h = ?, exposure = ? WHERE src = ?", (h,exp,src))
    else:
        c.execute("INSERT INTO calibrations VALUES (?, ?, ?)", (src, h, exp))

    conn.commit()
    conn.close()

def get_trafo(src):
    conn = sqlite3.connect('static/db/calibration.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("SELECT h FROM calibrations WHERE src = {}".format(src))
    h = c.fetchone()
    conn.close()

    if h is None:
        return None
    else:
        return h[0]

def get_exposure(src):
    conn = sqlite3.connect('static/db/calibration.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("SELECT exposure FROM calibrations WHERE src = {}".format(src))
    exposure = c.fetchone()
    conn.close()

    if exposure is None:
        return None
    else:
        return exposure[0]

if __name__ == '__main__':
    delete_db()
    create_db()

    exp = 5
    h = np.array([2,2])
    write_row(0, h, exp)
    
    exp = get_exposure(0)
    print(exp)