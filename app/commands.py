from app import app, db
from pathlib import Path
import os
import shutil


@app.cli.command("recreate-db")
def create_user():

    try:
        database_path = Path.cwd / 'app' / 'database.db'
        print(database_path)
        os.remove(database_path)
    except:
        print('No database found')

    pics_path = Path.cwd() / 'pics'
    [shutil.rmtree(pic) for pic in pics_path.glob('**/*')]
    db.create_all()
