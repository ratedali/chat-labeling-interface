from app import (
  auth,
  Conversation,
  Message,
)

# Create test user
def create_test_annotator():
  user = auth.User(username='user',
                   email='myahya@mtn.sd',
                   firstName='Mukhtar',
                   lastName='Yahya',
                   active=True)
  user.set_password('password')
  user.save()


if __name__ == "__main__":
  for model in (auth.User, Conversation, Message,):
    model.drop_table(fail_silently=True)
    model.create_table(fail_silently=True)
  create_test_annotator()
