from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mass_mail
from .models import Profile, Announcement, Event

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance, defaults={'role': Profile.ROLE_MEMBER})

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(post_save, sender=Announcement)
def notify_members_new_announcement(sender, instance, created, **kwargs):
    if created:
        # ONLY get users who have email_notifications = True
        recipient_list = list(User.objects.filter(
            is_active=True, 
            profile__email_notifications=True
        ).values_list('email', flat=True))
        
        recipient_list = [email for email in recipient_list if email]
        if not recipient_list: return

        author_name = instance.author.get_full_name() or instance.author.username
        subject = f"SportsCIO Announcement: {instance.title}"
        message = f"New announcement from {author_name}:\n\n{instance.title}\n\n{instance.content}"
        
        try:
            send_mass_mail(((subject, message, settings.DEFAULT_FROM_EMAIL, [e]) for e in recipient_list), fail_silently=True)
        except Exception as e:
            print(f"Error: {e}")

@receiver(post_save, sender=Event)
def notify_members_new_event(sender, instance, created, **kwargs):
    if created:
        # ONLY get users who have email_notifications = True
        recipient_list = list(User.objects.filter(
            is_active=True, 
            profile__email_notifications=True
        ).values_list('email', flat=True))
        
        recipient_list = [email for email in recipient_list if email]
        if not recipient_list: return

        author_name = instance.created_by.get_full_name() or instance.created_by.username
        start_str = instance.start_time.strftime("%B %d at %I:%M %p")
        subject = f"New Event: {instance.title}"
        message = f"{author_name} added an event: {instance.title}\nWhen: {start_str}\n\n{instance.description}"
        
        try:
            send_mass_mail(((subject, message, settings.DEFAULT_FROM_EMAIL, [e]) for e in recipient_list), fail_silently=True)
        except Exception as e:
            print(f"Error: {e}")