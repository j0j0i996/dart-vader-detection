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
            h array
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

def write_trafo(src, h):
    conn = sqlite3.connect('static/db/calibration.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("SELECT 1 FROM calibrations WHERE src = {}".format(src))
    resonse = c.fetchone()

    if resonse is not None:
        c.execute("UPDATE calibrations SET h = ? WHERE src = ?", (h,src))
    else:
        c.execute("INSERT INTO calibrations VALUES (?, ?)", (src,h))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    #delete_db()
    #create_db()

    #h = np.array([2,2])
    #write_trafo(10, h)
    h = get_trafo(4)
    print(h)