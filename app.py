#!/bin/env python3
import json
import flask
from peewee import *
from flask_peewee.db import Database
from flask_peewee.auth import Auth

bot_messages = {
  'العربيه',
  'العربية',
  'Get Started',
  'Unsubscribe',
}

# Set up flask application
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
app.config['DATABASE'] = {
  'name': 'labeled_data.db',
  'engine': 'peewee.SqliteDatabase',
}

db = Database(app)
auth = Auth(app, db, db_table='annotators')


class Conversation(db.Model):
  id = IntegerField(primary_key=True)
  annotator = ForeignKeyField(auth.User, backref='conversations', on_delete='SET NULL')
  completed = BooleanField(default=False)

class Message(db.Model):
  conversation = ForeignKeyField(Conversation, backref='messages')
  number = IntegerField()
  content = TextField()
  category = CharField(null=True)
  subcategory = CharField(null=True)


@app.route('/', methods=['GET', 'POST'])
@auth.login_required
def example():
  annotator = auth.get_logged_in_user()
  message = fetch_message(annotator)
  return flask.render_template('example.html',
                               message=message,
                               annotator=annotator)

@app.route('/submit', methods=['POST'])
def submit():
  print(f'form = {flask.request.form}')
  conv_id = int(flask.request.form['conv_id'])
  conversation = Conversation.get(id=conv_id)

  message_num = int(flask.request.form['message_num'])
  content = flask.request.form['message']
  message = Message(conversation=conversation,
                           number=message_num,
                           content=content)

  message.category = flask.request.form['category']
  message.subcategory = flask.request.form[message.category]
  message.save()
  return flask.redirect(flask.url_for('example'))

def fetch_message(annotator):
  """Fetch the next message the annotator needs to label"""
  conversation = fetch_conversation(annotator)
  if conversation is None:
    return None
  previous_num = (Message
                  .select(fn.Max(Message.number))
                  .where(Message.conversation == conversation)
                  .scalar())
  start = previous_num + 1 if previous_num is not None else 0
  conv_data = data[conversation.id]
  for num, message in enumerate(conv_data[start:]):
    sender = message[1]
    content = message[3]
    if (sender != 'MTN Sudan'
        and content not in bot_messages):
      return Message(conversation=conversation,
                     number=start+num,
                     content=content)
  conversation.completed = True
  conversation.save()
  return fetch_message(annotator)


def fetch_conversation(annotator):
  """Fetch the current conversation for an annotator"""
  # see if the annotator has incomplete work
  query = (Conversation
           .select()
           .where((Conversation.annotator == annotator) & (Conversation.completed == False))
           .order_by(Conversation.id))
  # in that case, get the first unfinished conversation
  for conversation in query:
    return conversation
  # otherwise fetch a new conversation
  # and add it to the database
  conv_id = 0
  prev_conv_id = (Conversation
                  .select(fn.Max(Conversation.id))
                  .scalar())
  if prev_conv_id is not None:
    conv_id = prev_conv_id + 1
  if conv_id < num_conversations:
    return Conversation.create(id=conv_id,
                               annotator=annotator,
                               completed=False)
  return None

# Load data
with open('data.json') as json_file:
  data = json.load(json_file)[1:]
num_conversations = len(data)


if __name__ == "__main__":
  for model in (auth.User, Conversation, Message):
    model.create_table(fail_silently=True)
  app.run(host='0.0.0.0', port=5000)
