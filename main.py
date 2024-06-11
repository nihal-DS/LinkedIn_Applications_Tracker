import imaplib
import email
import yaml
import re
from datetime import date
import pandas as pd

# Replace with actual yml here
with open("cred.yml") as f:  
    content = f.read()

my_credentials = yaml.load(content, Loader=yaml.FullLoader)

user, password = my_credentials["user"], my_credentials["password"]

imap_url = "imap.gmail.com"

my_mail = imaplib.IMAP4_SSL(imap_url)

my_mail.login(user, password)

my_mail.select("Inbox")

key = "FROM"
value = "jobs-noreply@linkedin.com"
_, data = my_mail.search(None, key, value)

mail_id_list = data[0].split()

msgs = []
for num in mail_id_list:
    typ, data = my_mail.fetch(num, "(RFC822)")
    msgs.append(data)

def df_extractor(msgs, your_name):                         # Mention your first name, same as LinkedIn first name
    date_col=[]; company_col=[]; role_col=[]; link_col=[]
    for e in msgs:
        e = email.message_from_bytes(e[0][1])
        if re.search(f"{your_name}, your application was sent to", e['subject']):
            date = e['date']
            for body in e.walk():
                if body.get_content_type() == "text/plain":
                    body = body.get_payload().split("\n")
                    if "-----" in body[2]:
                        role = body[3].rstrip()
                        company = body[4].rstrip()
                        link = body[7][10:].split("?")[0]
                    else:
                        role = body[2].rstrip()
                        company = body[3].rstrip()
                        link = body[6][10:].split("?")[0]      
                    date_col.append(date)
                    company_col.append(company)
                    role_col.append(role)
                    link_col.append(link)
    out_df = pd.DataFrame({"date":date_col, "company":company_col, "role":role_col, "link":link_col})
    out_df["date"] = pd.to_datetime(out_df['date'].str[5:-11].str.strip()).apply(lambda x: x.strftime("%d-%b-%Y") + " " + str(x)[-8:])
    return out_df

df = df_extractor(msgs)
df["platform"] = "LinkedIn"

df.to_csv(date.today().strftime("%d-%b-%Y")+".csv", index=False)
