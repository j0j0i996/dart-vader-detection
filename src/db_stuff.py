import sqlite3

conn = sqlite3.connect('static/db/camera.db')

c = conn.cursor()

# c.execute("""CREATE TABLE cameras (
#             src integer,
#             h blob,
#             base_img_path string
#             )
#             """)


#c.execute("INSERT INTO cameras VALUES (50, 'blob', 'static/jpg/base_img_0.jpg')")

c.execute("SELECT * FROM cameras WHERE src = 50")

print(c.fetchone())

conn.commit()

conn.close()