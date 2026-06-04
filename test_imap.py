import imaplib
import email
from email.header import decode_header

def decode_mime_words(header_value: str) -> str:
    if not header_value:
        return "N/A"
    try:
        decoded = decode_header(header_value)
        parts = []
        for text, charset in decoded:
            if isinstance(text, bytes):
                parts.append(text.decode(charset or 'utf-8', errors='ignore'))
            else:
                parts.append(str(text))
        return "".join(parts)
    except Exception as e:
        return header_value

def test_gmail_search():
    user = "nandhini9074@gmail.com"
    password = "fudx onzq vehv lrde"
    host = "imap.gmail.com"
    port = 993
    
    print(f"Connecting to {host}:{port}...")
    try:
        mail = imaplib.IMAP4_SSL(host, port)
        print("Connected! Attempting to login...")
        mail.login(user, password)
        print("Login successful!")
        mail.select("INBOX")
        
        # Broad server-side search across all emails in the INBOX for the term "Flink"
        print("Searching all INBOX emails for the text 'Flink'...")
        status, data = mail.search(None, 'TEXT "Flink"')
        
        if status == "OK" and data[0]:
            all_ids = data[0].split()
            print(f"Total matching emails found for 'Flink': {len(all_ids)}")
            
            # Fetch and print details for all matches
            for idx, msg_id in enumerate(all_ids, 1):
                h_status, h_data = mail.fetch(msg_id, "(BODY[HEADER.FIELDS (SUBJECT FROM DATE)])")
                if h_status != "OK" or not h_data or not h_data[0]:
                    continue
                header_msg = email.message_from_bytes(h_data[0][1])
                subject = decode_mime_words(header_msg.get("Subject", ""))
                sender = decode_mime_words(header_msg.get("From", ""))
                date_str = header_msg.get("Date", "N/A")
                print(f"{idx}. ID: {msg_id.decode()}, Date: {date_str}, Sender: {sender}, Subject: {subject}")
        else:
            print("No matching emails found for 'Flink'.")
            
        mail.logout()
    except Exception as e:
        print(f"Error during search: {e}")

if __name__ == "__main__":
    test_gmail_search()
