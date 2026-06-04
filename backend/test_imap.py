import imaplib

def test_gmail_login():
    user = "nandhini9074@gmail.com"
    password = "fudx onzq vehv lrde"
    host = "imap.gmail.com"
    port = 993
    
    print(f"Connecting to {host}:{port}...")
    try:
        mail = imaplib.IMAP4_SSL(host, port)
        print("Connected! Attempting to login...")
        mail.login(user, password)
        print("Login successful! Connection verified.")
        mail.select("INBOX")
        status, data = mail.search(None, "ALL")
        if status == "OK":
            print(f"Total emails found in inbox: {len(data[0].split())}")
        mail.logout()
    except Exception as e:
        print(f"Login failed: {e}")

if __name__ == "__main__":
    test_gmail_login()
