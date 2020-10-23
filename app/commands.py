from app import app, db
from pathlib import Path
import os
import shutil


@app.cli.command("recreate-db")
def recreate_db():

    try:
        database_path = Path.cwd() / 'app' / 'database.db'
        os.remove(str(database_path))
    except:
        print('No database found')

    db.create_all()


@app.cli.command("delete-pics")
def delete_pics():
    pics_path = Path.cwd() / 'pics'
    [shutil.rmtree(pic) for pic in pics_path.glob('**/*')]


@app.cli.command("recreate")
def recreate():
    recreate_db()
    delete_pics()
