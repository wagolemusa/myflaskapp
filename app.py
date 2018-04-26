from flask import Flask, request, render_template,flash,redirect, url_for, session, logging

from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = "my precious"


#Confing MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'refuge'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#init MYSQL
mysql = MySQL(app)


Articles = Articles()


@app.route('/')
def home():
	return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html')


@app.route('/articles')
def articles():
	return render_template('articles.html', articles = Articles)


@app.route('/article/<string:id>/')
def article(id):
	return render_template('articles.html', id=id)


class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email  = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password',[
			validators.DataRequired(),
			validators.EqualTo('confirm', message='Passwords do not match')
	])
	confirm = PasswordField('Confirm Password')



@app.route('/register', methods=['GET', 'POST'])
def register():
		form = RegisterForm(request.form)
		if request.method == 'POST' and form.validate():
			name = form.name.data
			username = form.username.data
			email = form.email.data
			password = sha256_crypt.encrypt(str(form.password.data))


			# Create cursor
			cur = mysql.connection.cursor()


			cur.execute("INSERT INTO users(name, username, email, password) VALUES(%s, %s, %s, %s)",(name,  username, email, password))

			#commit to DB
			mysql.connection.commit()

			# Close connection
			cur.close()

			flash('You are now register and log in', 'success')


			return redirect(url_for('login'))
		return render_template('register.html', form=form)

if __name__ == '__main__':
	app.run(debug=True)