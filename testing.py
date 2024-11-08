from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
password_hash = bcrypt.generate_password_hash('admin').decode('utf-8')
print(password_hash)