import emailer
import os

for filename in os.listdir("unsent"):
	emailer.send_email_for_file("unsent/"+filename)
	os.rename("unsent/"+filename, "sent/"+filename)
