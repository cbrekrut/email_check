import json
import imaplib
import email
from email.header import decode_header
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone
from dateutil import parser

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def receive(self, text_data):
        from .models import EmailAccount, EmailMessage, Attachment
        text_data_json = json.loads(text_data)
        email_address = text_data_json['email']
        password = text_data_json['password']
        
        # Сохраняю учетные данные в базу данных
        email_account, created = EmailAccount.objects.get_or_create(email=email_address)
        email_account.password = password  # В реальном проекте я бы не хранил открытым пароль
        email_account.save()

        # Получение доменного имени из email-адреса
        domain = email_address.split('@')[-1]
        
        # Карта для доменов и их IMAP-серверов
        imap_servers = {
            "gmail.com": "imap.gmail.com",
            "yahoo.com": "imap.mail.yahoo.com",
            "outlook.com": "imap-mail.outlook.com",
            "hotmail.com": "imap-mail.outlook.com",
            "aol.com": "imap.aol.com",
            "yandex.ru": "imap.yandex.ru",
        }

        # Получаем IMAP сервер на основе домена
        imap_server = imap_servers.get(domain)

        if not imap_server:
            # Если домен не поддерживается, отправляем ошибку
            self.send(text_data=json.dumps({
                'type': 'error',
                'message': f"IMAP сервер для домена {domain} не найден"
            }))
            return
        
        # Подключение к почтовому серверу
        mail = imaplib.IMAP4_SSL(imap_server)
        try:
            mail.login(email_address, password)
            mail.select("inbox")
            result, data = mail.search(None, "ALL")

            # Получение списка идентификаторов сообщений
            mail_ids = data[0].split()
            total_emails = 100
            emails = []

            # Перебираю все письма
            for idx, mail_id in enumerate(mail_ids[-100:], start=1):
                result, msg_data = mail.fetch(mail_id, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Декодирование заголовков
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else 'utf-8')
                
                # Использую dateutil.parser для парсинга даты
                date_sent_str = msg["Date"]
                try:
                    date_sent = parser.parse(date_sent_str)
                except (ValueError, TypeError) as e:
                    date_sent = timezone.now() 
                
                date_received = timezone.now()

                # Сохраняем сообщение в базу данных
                email_message = EmailMessage.objects.create(
                    email_account=email_account,
                    subject=subject,
                    date_sent=date_sent,
                    date_received=date_received,
                    body=msg.get_payload()
                )

                # Работа с вложениями
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_maintype() == 'multipart':
                            continue
                        if part.get('Content-Disposition') is None:
                            continue

                        file_name = part.get_filename()
                        if file_name:
                            file_data = part.get_payload(decode=True)
                            Attachment.objects.create(
                                email_message=email_message,
                                file_name=file_name,
                                file_data=file_data
                            )

                emails.append({
                    "subject": subject,
                    "date": date_sent_str,
                    "from": msg["From"],
                    "to": msg["To"]
                })
                
                # Отправка прогресса на фронтэнд
                progress = (idx / total_emails) * 100
                self.send(text_data=json.dumps({
                    'type': 'progress',
                    'progress': progress
                }))
            
            # Отправка всех писем на фронтэнд после завершения загрузки
            self.send(text_data=json.dumps({
                'type': 'email_list',
                'emails': emails
            }))
        except imaplib.IMAP4.error as e:
            self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
        finally:
            mail.logout()
