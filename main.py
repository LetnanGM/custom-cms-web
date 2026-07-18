from flask import Flask, render_template, request
from pathlib import Path
from datetime import datetime

from typing import Tuple, List
from sqlite3 import Connection, connect, DatabaseError, Row

import markdown
import markdownify

import textwrap

app = Flask(__name__)

def paragraf_handler(text: str) -> str:
    paragraph = text.split("\n\n")
    new_paragraphs = []
    
    for p in paragraph:
        if p.startswith(('#', '-', '*', '>', '```', '|', '`')):
            new_paragraphs.append(p)
            
        else:
            wrapped = textwrap.fill(p, width=88)
            new_paragraphs.append(wrapped)
            
    return "\n\n".join(new_paragraphs)

def resolve_file_article(path: Path) -> bool:
    suffix: str = ".md"
    if not path.is_file():
        with open(str(path.resolve()), "w") as fp:
            fp.write("")
    
    if path.suffix == suffix:
        return True
    
    return False

class database:
    DB_FILE: str = "article.db"
        
    def get_conn(self):
        conn: Connection = connect(database="article.db")
        conn.row_factory = Row
        return conn
        
    def create_table(self, table_name: str) -> bool:
        with self.get_conn() as conn:
            conn.execute(f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        judul TEXT NOT NULL,
        content TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
            """)
            conn.commit()
        
    def insert_artikel(self, judul: str, artikel: str, id: str = None) -> Tuple[bool, str]:
        if not judul:
            raise ValueError("judul diperlukan!")
        
        if not artikel:
            raise ValueError("artikel diperlukan!")
        
        import os
        
        os.makedirs("./md", exist_ok=True)
        
        path = Path(artikel)
        response =  resolve_file_article(path)
        
        if not response:
            return False, "file tidak cocok dengan persyaratan sistem"
        
        try:
            if not id:
                with self.get_conn() as conn:
                    artikel = os.path.join("./md", artikel)
                    conn.execute("""
                INSERT INTO posts (judul, content) VALUES (?, ?)
                    """, (judul, artikel))
                    conn.commit()
                    return True, "Berhasil dimasukan!"
            
            with self.get_conn() as conn:
                conn.execute("""
        INSERT INTO posts (id, judul, content)
        VALUES (?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            judul = excluded.judul,
            content = excluded.content,
            updated_at = CURRENT_TIMESTAMP
        """, (id, judul, artikel)
                )
                conn.commit()
                return True, "Berhasil di input"

        except DatabaseError as e:
            print(f"[!] Server error > {e}")
    
    def delete(self, id: str):
        with self.get_conn() as conn:
            conn.execute(
                """
    DELETE FROM posts
    WHERE id = ?
                """, (id,),
            )
            conn.commit()
        
    def query_content_by_id(self, id: str) -> Row:
        with self.get_conn() as conn:
            return conn.execute("""
        SELECT * FROM posts
        WHERE id = ?
                            """, (id,),).fetchone()
            
    
    def fetch_all(self) -> List[Row]:
        with self.get_conn() as conn:
            return list(conn.execute("""
        SELECT * FROM posts                 
            """))
            
db = database()
db.create_table("posts")

def parsing_time(time: str) -> datetime:
    """
    2026-07-07 07:36:38
    """
    return datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

def parse_datetime(target_time: datetime):
    date = {
        1: 'January', 
        2: 'February', 
        3: 'March', 
        4: 'April', 
        5: 'May', 
        6: 'June', 
        7: 'July', 
        8: 'August', 
        9: 'September', 
        10: 'October',
        11: 'November', 
        12: 'December'
    }
    
    current_month = target_time.month
    if current_month in date:
        
        return date.get(current_month)

def susun_tanggal(time: str) -> str:
    datetime = parsing_time(time=time)
    month = parse_datetime(datetime)
    
    return f"{month} {datetime.day}, {datetime.year}"

@app.route("/")
def index() -> None:
    return render_template("index.html", articles=db.fetch_all(), date=susun_tanggal)

@app.route("/article/<int:id>")
def view(id: int):
    
    data = db.query_content_by_id(id=id)
    date = susun_tanggal(data["created_at"])
    
    judul = data["judul"]
    with open(data["content"], "r", encoding="utf-8", errors="replace") as fp:
        md = markdown.markdown(fp.read(), extensions=["tables", "fenced_code"])
    
    return render_template("view.html", article=md, judul=judul, tanggal_rilis=date)

@app.route("/admin")
def dashboard():
    return render_template("admin.html", articles=db.fetch_all())

@app.route("/edit/<int:id>")
def edit_article(id: int):

    data = db.query_content_by_id(id=id)
    date = susun_tanggal(data["created_at"])
    
    judul = data["judul"]
    with open(data["content"], "r", encoding="utf-8", errors="replace") as fp:
        md = markdown.markdown(textwrap.fill(fp.read(), width=88), extensions=["tables", "fenced_code"])
    
    return render_template("edit.html", id=id, article=md, judul=judul, tanggal_rilis=date)

@app.route("/new")
def new_article():
    return render_template("new.html")

@app.route("/edit/go/<int:id>", methods=["POST"])
def api_edit(id: int):
    judul = request.form.get("judul")
    date = request.form.get("date_release")
    content = request.form.get("content")
    
    md = db.query_content_by_id(id=id)
    file = md['content']
    response, reason = db.insert_artikel(id=id, judul=judul, artikel=file)
    
    with open(f"{file}", "w", encoding="utf-8") as fp:
        fp.write(textwrap.fill(markdownify.markdownify(content), width=88))
        
    return "Successfully edited!" if response else reason

@app.route("/new/go", methods=["POST"])
def api_new():
    import random
    
    judul = request.form.get("judul")
    date = request.form.get("date_release")
    content = request.form.get("content")
    
    file = ''.join([str(random.randint(1, 255)) for _ in range(8)]) + ".md"
    
    response, reason = db.insert_artikel(judul=judul, artikel=file)
    with open(f"./md/{file}", "w", encoding="utf-8", errors="replace") as fp:
        fp.write(content)
            
    return "Successfully registered!" if response else reason

if __name__ == '__main__':    
    app.run(debug=True)