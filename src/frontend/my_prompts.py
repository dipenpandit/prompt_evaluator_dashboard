from db.database import get_db
from db.models import Prompt

db = next(get_db())

prompts = db.query(Prompt).all()    