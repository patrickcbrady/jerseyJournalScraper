import emailer
import os

def send_file(filename):
    print(f'sending file {filename}')
    #emailer.test_categories('unsent/' + filename)
    try:
        emailer.send_email_for_file('unsent/'+filename)
        os.rename('unsent/'+filename, 'sent/'+filename)
    except Exception as e:
        print(f"Something went wrong: {e}")

unsent_file_names = [f_name for f_name in os.listdir('unsent')]

for filename in unsent_file_names:
    send_file(filename)
