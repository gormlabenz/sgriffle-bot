from app import app, db
import os


@app.cli.command("recreate-db")
def create_user():
    try:
        os.remove('./app/database.db')
    except:
        print('No database found')
    db.create_all()
