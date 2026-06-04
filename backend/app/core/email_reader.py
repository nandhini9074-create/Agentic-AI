import os
import imaplib
import email
from email.header import decode_header
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re
import base64

logger = logging.getLogger("certificate_intelligence.email_reader")

KEYWORDS = [
    "certificate", "completion", "workshop", "internship", "hackathon", 
    "training", "course", "webinar", "credential", "publication", 
    "published", "award", "recognition", "participation", "event",
    "achievement", "bootcamp", "program", "scholar"
]

class EmailReader:
    def __init__(self):
        self.host = os.getenv("EMAIL_HOST", "imap.gmail.com")
        self.port = int(os.getenv("EMAIL_PORT", "993"))
        self.user = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASSWORD")

        if not self.user or not self.password:
            # Fallback check
            self.user = os.environ.get("EMAIL_USER")
            self.password = os.environ.get("EMAIL_PASSWORD")

        if not self.user or not self.password:
            logger.warning("Email credentials (EMAIL_USER/EMAIL_PASSWORD) are not configured. Email extraction will be bypassed.")

    def _decode_mime_words(self, header_value: str) -> str:
        """Decode multi-part MIME encoded words in subject/sender headers."""
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
            logger.warning(f"Error decoding MIME header: {e}")
            return header_value

    def _clean_html(self, html_content: str) -> str:
        """Strip HTML tags and CSS blocks to retrieve clean, readable text."""
        # Remove script and style elements
        text = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', html_content)
        text = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', text)
        # Convert break tags and paragraph tags to newlines
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'</p>', '\n', text)
        # Strip all other HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Consolidate spaces and newlines
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()

    def _extract_body_text(self, msg: email.message.Message) -> str:
        """Walk through email structures and extract clean text bodies."""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                if content_type == "text/plain":
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        body += part.get_payload(decode=True).decode(charset, errors='ignore') + "\n"
                    except Exception as e:
                        logger.warning(f"Error reading plain text part: {e}")
                elif content_type == "text/html" and not body:
                    # If we haven't found plain text, we take HTML and strip tags
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        html_text = part.get_payload(decode=True).decode(charset, errors='ignore')
                        body += self._clean_html(html_text) + "\n"
                    except Exception as e:
                        logger.warning(f"Error reading HTML part: {e}")
        else:
            content_type = msg.get_content_type()
            try:
                charset = msg.get_content_charset() or 'utf-8'
                payload = msg.get_payload(decode=True).decode(charset, errors='ignore')
                if content_type == "text/html":
                    body = self._clean_html(payload)
                else:
                    body = payload
            except Exception as e:
                logger.error(f"Error reading singlepart body: {e}")
        return body.strip()

    def _extract_attachments(self, msg: email.message.Message) -> List[str]:
        """Walk through email structures and extract attachment filenames."""
        attachments = []
        if msg.is_multipart():
            for part in msg.walk():
                filename = part.get_filename()
                if filename:
                    decoded = self._decode_mime_words(filename)
                    if decoded and decoded != "N/A":
                        attachments.append(decoded)
        else:
            filename = msg.get_filename()
            if filename:
                decoded = self._decode_mime_words(filename)
                if decoded and decoded != "N/A":
                    attachments.append(decoded)
        return attachments

    def _generate_oauth2_string(self, username: str, access_token: str) -> bytes:
        """Generate the OAuth2 string for IMAP authentication."""
        auth_string = f"user={username}\1auth=Bearer {access_token}\1\1"
        return auth_string.encode('utf-8')

    def _jaccard_similarity(self, str1: str, str2: str) -> float:
        """Calculate word-level Jaccard similarity between two strings."""
        words1 = set(re.findall(r'\w+', str1.lower()))
        words2 = set(re.findall(r'\w+', str2.lower()))
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union)



    def _fetch_emails_sync(
        self, 
        months_back: int = 12, 
        cert_data: Optional[Any] = None, 
        filename: Optional[str] = None,
        raw_ocr_text: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Synchronous IMAP operation to connect, search, and extract relevant emails."""
        login_user = user_email if user_email else self.user
        
        # Look up OAuth token in database
        oauth_token_record = None
        if login_user:
            try:
                from app.models.database import SessionLocal, OAuthToken
                db = SessionLocal()
                oauth_token_record = db.query(OAuthToken).filter(
                    (OAuthToken.email == login_user) | (OAuthToken.user_id == login_user)
                ).first()
                db.close()
            except Exception as e:
                logger.error(f"Failed to lookup OAuth token for {login_user}: {e}")
        
        if not oauth_token_record and (not login_user or not self.password):
            logger.info("Email credentials (OAuth Token or EMAIL_USER/EMAIL_PASSWORD) are not configured. Skipping email matching.")
            return []

        # Build dynamic keywords list based on uploaded certificate
        dynamic_keywords = list(KEYWORDS)
        
        if cert_data:
            # Extract key terms from certificate name
            cert_name = getattr(cert_data, "certificate_name", "")
            if cert_name and cert_name.strip() and cert_name.lower() not in {"n/a", "unknown", "extraction failed"}:
                words = [re.sub(r'\W+', '', w).lower() for w in cert_name.split()]
                words = [w for w in words if len(w) > 3 and w not in {"with", "this", "that", "your", "from", "have", "certificate"}]
                dynamic_keywords.extend(words)
                dynamic_keywords.append(cert_name.lower())
            
            # Extract key terms from issuer name
            issuer = getattr(cert_data, "issuer", "")
            if issuer and issuer.strip() and issuer.lower() not in {"n/a", "unknown", "extraction failed"}:
                words = [re.sub(r'\W+', '', w).lower() for w in issuer.split()]
                words = [w for w in words if len(w) > 3 and w not in {"with", "this", "that", "your", "from", "have", "corporation", "company", "limited", "incorporated"}]
                dynamic_keywords.extend(words)
                dynamic_keywords.append(issuer.lower())

            # Extract key terms from skills
            skills = getattr(cert_data, "skills", [])
            for skill in skills:
                if skill and skill.strip():
                    words = [re.sub(r'\W+', '', w).lower() for w in skill.split()]
                    words = [w for w in words if len(w) > 3]
                    dynamic_keywords.extend(words)
                    dynamic_keywords.append(skill.lower())

        if filename:
            # Strip extension and split by delimiters
            base_name = os.path.splitext(filename)[0]
            words = [re.sub(r'\W+', '', w).lower() for w in re.split(r'[_-\s]', base_name)]
            words = [w for w in words if len(w) > 3 and w not in {"certificate", "receipt", "invoice", "upload", "scan", "copy", "n/a", "unknown", "extraction failed"}]
            dynamic_keywords.extend(words)
            dynamic_keywords.append(base_name.lower())
            
        # De-duplicate keywords and filter out empty strings & generic N/A terms
        dynamic_keywords = list(set([
            kw.strip().lower() 
            for kw in dynamic_keywords 
            if kw and len(kw.strip()) > 2 and kw.strip().lower() not in {"n/a", "unknown", "extraction failed", "nan"}
        ]))
        logger.info(f"Using dynamic keywords for email filtering: {dynamic_keywords[:15]}... (Total: {len(dynamic_keywords)})")

        fetched_emails = []
        mail = None
        try:
            logger.info(f"Connecting to IMAP Server: {self.host}:{self.port} with user: {login_user}...")
            mail = imaplib.IMAP4_SSL(self.host, self.port)
            
            # Authenticate via XOAUTH2 if token exists, else standard login
            if oauth_token_record and oauth_token_record.access_token:
                logger.info(f"Using XOAUTH2 authentication for {login_user}")
                mail.authenticate('XOAUTH2', lambda x: self._generate_oauth2_string(login_user, oauth_token_record.access_token))
            else:
                logger.info(f"Using standard Password authentication for {login_user} (Fallback Mode)")
                mail.login(login_user, self.password)
                
            mail.select("INBOX")

            # Calculate the date range for search (SINCE)
            since_date = (datetime.now() - timedelta(days=30 * months_back)).strftime("%d-%b-%Y")
            
            matching_message_ids = set()
            
            # 1. Search by date (primary filter)
            logger.info(f"Searching IMAP Inbox since {since_date}...")
            status, data = mail.search(None, f'(SINCE "{since_date}")')
            
            if status == "OK" and data[0]:
                all_ids = data[0].split()
                # To optimize, we take the most recent 150 emails
                recent_ids = all_ids[-150:]
                
                logger.info(f"Analyzing {len(recent_ids)} recent email headers for keywords...")
                
                # Fetch headers in bulk to filter keywords
                for msg_id in reversed(recent_ids):
                    # Fetch only the headers first (Envelope) to save bandwidth
                    h_status, h_data = mail.fetch(msg_id, "(BODY[HEADER.FIELDS (SUBJECT FROM DATE)])")
                    if h_status != "OK" or not h_data or not h_data[0]:
                        continue
                        
                    header_msg = email.message_from_bytes(h_data[0][1])
                    subject = self._decode_mime_words(header_msg.get("Subject", ""))
                    sender = self._decode_mime_words(header_msg.get("From", ""))
                    
                    # Check if any of our dynamic keywords are in the subject line or sender address (case-insensitive)
                    subject_lower = subject.lower()
                    sender_lower = sender.lower()
                    if any(kw in subject_lower or kw in sender_lower for kw in dynamic_keywords):
                        matching_message_ids.add(msg_id)
            
            logger.info(f"Found {len(matching_message_ids)} relevant emails matching keywords.")
            
            # 2. Fetch full body of only the matching emails
            for msg_id in matching_message_ids:
                b_status, b_data = mail.fetch(msg_id, "(RFC822)")
                if b_status != "OK" or not b_data or not b_data[0]:
                    continue
                
                raw_email = b_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                subject = self._decode_mime_words(msg.get("Subject"))
                sender = self._decode_mime_words(msg.get("From"))
                date_str = msg.get("Date")
                body = self._extract_body_text(msg)
                attachments = self._extract_attachments(msg)
                
                # Match attachment check
                has_matching_attachment = False
                if filename:
                    fn_lower = filename.lower()
                    for att in attachments:
                        att_lower = att.lower()
                        if fn_lower in att_lower or att_lower in fn_lower or self._jaccard_similarity(fn_lower, att_lower) > 0.6:
                            has_matching_attachment = True
                            break

                fetched_emails.append({
                    "id": msg_id.decode('utf-8', errors='ignore'),
                    "subject": subject,
                    "sender": sender,
                    "date": date_str,
                    "body": body,
                    "attachments": attachments,
                    "has_matching_attachment": has_matching_attachment
                })
                
                # Cap the maximum emails to process in single run to avoid LLM tokens blowup
                if len(fetched_emails) >= 15:
                    logger.info("Capping email processing count at 15 matching messages.")
                    break

        except Exception as e:
            logger.error(f"IMAP Email connection or extraction failed: {e}")
        finally:
            if mail:
                try:
                    mail.close()
                    mail.logout()
                except Exception:
                    pass
                    
        return fetched_emails

    async def fetch_recent_emails(
        self, 
        months_back: int = 12, 
        cert_data: Optional[Any] = None, 
        filename: Optional[str] = None,
        raw_ocr_text: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Asynchronously fetch recent relevant emails.
        Executes blocking IMAP socket operations in a separate thread pool to preserve event loop speed.
        """
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(None, self._fetch_emails_sync, months_back, cert_data, filename, raw_ocr_text, user_email)
        except Exception as e:
            logger.error(f"Error in async email fetch wrapper: {e}")
            return []
