from flask import Flask
from mod_categories import category

app = Flask(__name__)

if __name__ == '__main__':
	app.register_blueprint(category)
	app.debug = True
	app.run(host='0.0.0.0', port=5000)