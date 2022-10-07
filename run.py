from app import app
from app import db

if __name__ == '__main__':
	with app.app_context():
		db.init_app(app)
		db.create_all()
	app.run(host='0.0.0.0', port=8000, debug=True)
