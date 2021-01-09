import mysql.connector
import json

data_filter = 'العربيه'

#fetch the filtered line
def fetch_line(line_num, conv):
   new_line_num = line_num
  # print(line_num)
   for line in conv[line_num:]:
     new_line_num += 1  
     if 'MTN Sudan' not in line[1]:
       print(any(data_filter) == line[1])  
       print(line)
       return line[3],new_line_num
   return 'empty', 0


#set up the database
db = mysql.connector.connect(host='34.91.135.43',user='root',passwd='',database='mtn_db')
mycursor = db.cursor(buffered=True)

#setup mtn_data
json_file = open('mtn_data.json')
data = json.load(json_file)

# ///////////// Request ////////////////////
#get conversation number with username and ended = false
username = input("username: ")
mycursor.execute("SELECT conv_num,line_num FROM request_manager WHERE username = %s AND ended = false",(username,))
query = mycursor.fetchone()
#print(query)

# if the username dont have ended = false (does not have a nonfinished conversation) take a new conversation and create its entry
if not query:
   mycursor.execute("SELECT MAX(conv_num) FROM request_manager")
   conv_num = mycursor.fetchone()[0] + 1
   line_num = 0
   mycursor.execute("INSERT INTO request_manager (username,conv_num,line_num,ended) VALUES (%s,%s,%s,%s)",(username,conv_num,line_num,0))
   db.commit()
#if ended = true we fetch conv_num and line_num
else:
   conv_num = query[0]
   line_num = query[1]
  # print(line_num)
   
#get the conversation from json file
conv = data[conv_num]
output_line,line_num = fetch_line(line_num, conv)
print(output_line)
label = input('label: ')
mycursor.execute("INSERT INTO labeled_data (conv_num,agent,text, label) VALUES (%s,%s,%s,%s)",(conv_num,username,output_line,label))
mycursor.execute("UPDATE request_manager SET line_num = %s WHERE conv_num = %s",(line_num,conv_num,))
db.commit()

if line_num >= len(conv):
   mycursor.execute("UPDATE request_manager SET ended = %s WHERE conv_num = %s",(1,conv_num,))
   db.commit()
