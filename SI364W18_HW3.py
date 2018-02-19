## SI 364 - Winter 2018
## HW 3

####################
## Import statements
####################

from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell

############################
# Application configurations
############################
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string from si364'
## TODO 364: Create a database in postgresql in the code line below, and fill in your app's database URI. It should be of the format: postgresql://localhost/YOUR_DATABASE_NAME

## Your final Postgres database should be your uniqname, plus HW3, e.g. "jczettaHW3" or "maupandeHW3"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://vinhluong@localhost/vinhblHW3"
## Provided:
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##################
### App setup ####
##################
db = SQLAlchemy(app) # For database use
manager = Manager(app)


#########################
#########################
######### Everything above this line is important/useful setup,
## not problem-solving.##
#########################
#########################

#########################
##### Set up Models #####
#########################

## TODO 364: Set up the following Model classes, as described, with the respective fields (data types).

class Tweet(db.Model):
    __tablename__ = "Tweets"
    tweet_id = db.Column(db.Integer, primary_key=True)
    text = (db.Column(db.String(280)))
    user_id = (db.Column(db.Integer, db.ForeignKey("Users.account_id")))

    def __repr__(self):
        return "Tweet text: {} (ID: {})".format(self.text, self.tweet_id)

class User(db.Model):
    __tablename__ = "Users"
    account_id = db.Column(db.Integer, primary_key=True)
    username = (db.Column(db.String(64)))
    display_name = (db.Column(db.String(124)))

    def __repr__(self):
        return "{} | ID: {})".format(self.username, self.account_id)

########################
##### Set up Forms #####
########################

class TweetForm(FlaskForm):
    text = StringField("Enter the text of the tweet (no more than 280 chars):", validators=[Required(),Length(max=280, message="Tweet must be no longer than 250 characters!")])
    username = StringField("Enter the username of the twitter user (no '@' symbols!'):", validators=[Required(),Length(max=64, message="Your must not have an '@' symbol in your username!"),])
    display_name = StringField("Enter the display name for the twitter user (must be at least 2 words):", validators=[Required(),Length(max=64, message="Your must not have an '@' symbol in your username!"),])
    submit = SubmitField("Submit")
    
    def validate_username(self, field):
        if "@" in field.data:
            raise ValidationError("Your display name may not contain any '@' symbols!")

    def validate_display_name(self, field):
        if len(field.data.split()) < 2:
            raise ValidationError("Your display name must be at least two words!")


###################################
##### Routes & view functions #####
###################################

## Error handling routes - PROVIDED
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#############
## Main route
#############


@app.route('/', methods=['GET', 'POST'])
def index():
    form = TweetForm()
    num_tweets = len(Tweet.query.all())
    if form.validate_on_submit():
        tweet = form.text.data
        username = form.username.data
        display_name = form.display_name.data
        if User.query.filter_by(username=username).first():
            user = User.query.filter_by(username=username).first()
            print("User already exists!")
        else:
            user = User(username=username, display_name=display_name)
            db.session.add(user)
            db.session.commit()
        if (Tweet.query.filter_by(text=tweet, user_id=user.account_id).first()):
            return redirect(url_for("see_all_tweets"))
        else:
            post = Tweet(text=tweet, user_id=user.account_id)
            db.session.add(post)
            db.session.commit()
            flash("Tweet successfully saved!")
            return redirect(url_for("index"))

    # PROVIDED: If the form did NOT validate / was not submitted
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('index.html', form=form, num_tweets=num_tweets) # TODO 364: Add more arguments to the render_template invocation to send data to index.html

@app.route('/all_tweets')
def see_all_tweets():
    all_tweets = []
    twts = Tweet.query.all()
    for i in twts:
        user = User.query.filter_by(account_id=i.user_id).first()
        all_tweets.append((i.text, user.username))
    return render_template("all_tweets.html", all_tweets=all_tweets)

@app.route('/all_users')
def see_all_users():
    users = User.query.all()
    return render_template("all_users.html", users=users)

@app.route('/longest_tweet')
def get_longest_tweet():
    tweets = Tweet.query.all()
    longest = ''
    count = 0
    for i in tweets:
        if len(''.join(i.text.split())) > count:
            count = len(''.join(i.text.split()))
            longest = i.text
    return render_template("longest_tweet.html", tweet=longest)


if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual
