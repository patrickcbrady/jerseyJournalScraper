import smtplib
import week

gmail_user = open('./deviceu','r').read().replace('\n','')
gmail_pw = open('./devicepw','r').read().replace('\n','')

sent_from = gmail_user
to = [gmail_user]
subject = "Weehawken Public Notices for Week of %s" % (week.getCurrentWeek())
body = open('./'+week.getCurrentWeek()).read()

email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

try:
	server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	server.ehlo()
	server.login(gmail_user, gmail_pw)
	server.sendmail(sent_from, to, email_text)
	server.close()

	print 'Email sent Successfully for', week.getCurrentWeek()
except Exception as e:
	print 'Something went wrong:', e

