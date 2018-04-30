from flask import Flask, request, render_template,flash,redirect, url_for, session, logging

from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools	import wraps

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


#Cheack if user loggged_in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
			
		else:
			flash('Unauthorized, Please login', 'danger')
			return redirect(url_for('login'))
	return wrap


# index page
@app.route('/')
def home():
	return render_template('home.html')

#about
@app.route('/about')
def about():
	return render_template('about.html')


# logout
@app.route('/logout')
def logout():
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	return render_template('dashboard.html')

# article routes
@app.route('/articles')
def articles():
	return render_template('articles.html', articles = Articles)

# Single Article
@app.route('/article/<string:id>/')
def article(id):
	return render_template('articles.html', id=id)


# registration form class
class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email  = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password',[
			validators.DataRequired(),
			validators.EqualTo('confirm', message='Passwords do not match')
	])
	confirm = PasswordField('Confirm Password')


# user register
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
		
# end of registraiton form

# USER LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		#Get form field
		username = request.form['username']
		password_candidate = request.form['password']

		#Create cursor

		cur = mysql.connection.cursor()

		#Get user by username
		result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

		if result > 0:
			#Get stored hash
			data = cur.fetchone()
			password = data['password']

			#Compare password

			if sha256_crypt.verify(password_candidate, password):

				# Passed
				session['logged_in'] = True
				session['username']  = username

				flash('You are now logged in', 'success')
				return redirect(url_for('dashboard'))

			else:
				error = 'Invalid login'
				return render_template('login.html', error=error)

			#Close connetion
			cur.close()
		else:
			error = 'username not found'
			return render_template('login.html', error=error)

	return  render_template('login.html')



if __name__ == '__main__':
	app.run(debug=True)