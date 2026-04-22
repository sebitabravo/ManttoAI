from app.database import SessionLocal
from app.models.usuario import Usuario
from app.services.auth_service import hash_password

db = SessionLocal()
u = Usuario(email='admin@mantto.ai', password_hash=hash_password('admin123'), nombre='Admin', rol='admin', onboarding_completed=False, onboarding_step=1)
db.add(u)
db.commit()
print('User created!')
