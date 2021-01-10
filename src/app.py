import json
from flask import (
    Flask,
    Response,
    request,
    render_template,
)
from peewee import *

db = SqliteDatabase('labeled_data.db')


class BaseModel(Model):
  class Meta:
    database = db

class Annotator(BaseModel):
  username = CharField(unique=True)
  firstName = CharField()
  lastName = CharField()

class Conversation(BaseModel):
  id = IntegerField(primary_key=True)
  annotator = ForeignKeyField(Annotator, backref='conversations', on_delete='SET NULL')
  completed = BooleanField(default=False)

class Message(BaseModel):
  conversation = ForeignKeyField(Conversation, backref='messages')
  number = IntegerField()
  content = TextField()
  category = CharField(null=True)
  subcategory = CharField(null=True)

app = Flask(__name__)
db.connect()
db.create_tables([Annotator, Conversation, Message])
annotator, _created = Annotator.get_or_create(username="annotator123", defaults={"firstName": "Mukhtar", "lastName": "Yahya"})


with open('mtn_data.json') as json_file:
  data = json.load(json_file)

@app.route('/')
def example():
  conversation = None
  # see if the annotator has incomplete work
  query = (Conversation
           .select()
           .where((Conversation.annotator == annotator) & (Conversation.completed == False))
           .order_by(Conversation.id))
  # in that case, get the first unfinished conversation
  for convo in query:
      conversation = convo
      break
  # otherwise fetch a new conversation
  if conversation is None:
    # add the conversation to the database
    conversation = Conversation.create(id=1, annotator=annotator, completed=False)
  # find the number of the message to be fetched
  message = None
  message_number = 1
  for m in reversed(conversation.messages):
    message_number = m.number
    if m.category is None:
      message = m
      message_number = m.number
      break
    if m.category is not None:
      message_number += 1
  # fetch an unlabled message and show it to the annotator
  if message is None:
    message = Message.create(conversation=conversation, number=message_number, content=f"خدمات النت {message_number}")
  return render_template('example.html', annotator=annotator, conversation=conversation, message=message)

@app.route('/submit', methods=['POST'])
def submit():
  print(request.form['messageNumber'])
  convo_id = request.form['conversationId']
  conversation = Conversation.get(id=convo_id)

  message_number = request.form['messageNumber']
  message = Message.get(conversation=conversation, number=message_number)

  message.category = request.form['category']
  if 'subcategory' in request.form:
    message.subcategory = request.form['subcategory']
  message.save()
  return Response(status=200)
