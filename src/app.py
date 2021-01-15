import json
from flask import *
from peewee import *

bot_messages = {
  'العربيه',
  'العربية',
  'Get Started',
  'Unsubscribe',
}

#set up the database
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

# Test Annotator
annotator, _created = Annotator.get_or_create(username="annotator123", defaults={"firstName": "Mukhtar", "lastName": "Yahya"})

# Load data
with open('data.json') as json_file:
  data = json.load(json_file)[1:]
num_conversations = len(data)

@app.route('/')
def example():
  message = fetch_message(annotator)
  return render_template('example.html',
                         message=message,
                         annotator=annotator)


@app.route('/submit', methods=['POST'])
def submit():
  conv_id = int(request.form['conv_id'])
  conversation = Conversation.get(id=conv_id)

  message_num = int(request.form['message_num'])
  content = request.form['message']
  message = Message(conversation=conversation,
                           number=message_num,
                           content=content)

  message.category = request.form['category']
  if 'subcategory' in request.form:
    message.subcategory = request.form['subcategory']
  message.save()

  return Response(status=200)


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

