from django.db import models

class EmailAccount(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # В продакшене я бы шифровал пароли

    def __str__(self):
        return self.email

class EmailMessage(models.Model):
    email_account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE, related_name="messages")
    subject = models.CharField(max_length=255)
    date_sent = models.DateTimeField()
    date_received = models.DateTimeField()
    body = models.TextField()
    
    def __str__(self):
        return f"Message from {self.email_account.email}: {self.subject}"

class Attachment(models.Model):
    email_message = models.ForeignKey(EmailMessage, on_delete=models.CASCADE, related_name="attachments")
    file_name = models.CharField(max_length=255)
    file_data = models.BinaryField()

    def __str__(self):
        return f"Attachment: {self.file_name}"
