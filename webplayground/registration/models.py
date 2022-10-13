from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

def custom_upload_to(instance, filename):
    # Obtenemos la instancia antes de ser modificado, usando para ello su Primary Key.
    old_instance = Profile.objects.get(pk=instance.pk)
    # Borra el avatar original.
    old_instance.avatar.delete()
    # Devuelve la ruta donde se guardará el nuevo avatar.
    return 'profiles/' + filename

# Create your models here.
class Profile(models.Model):
    # OneToOne significa que la relacion de Profile con el user es de 1 a 1.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='custom_upload_to', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    link = models.URLField(max_length=200, null=True, blank=True)

    class Meta:
        ordering = ['user__username']


# Esta señal (signal) se ejecutará en el momento en el que se guarde el usuario.
@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, **kwargs):

    if kwargs.get('created', False):
        Profile.objects.get_or_create(user=instance)
        #print("Se acaba de crear un usuario y su perfil enlazado.")