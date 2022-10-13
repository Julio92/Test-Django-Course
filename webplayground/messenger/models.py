from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed

# Create your models here.
class Message(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']


class ThreadManager(models.Manager):

    def find(self, user1, user2):
        # Filtramos sobre todos los hilos existentes por usuarios.
        querySet = self.filter(users=user1).filter(users=user2)

        if len(querySet) > 0:
            # Si la longitud del set es mayor que 0, significa que hemos encontrado el hilo.
            return querySet[0]

        return None

    def find_or_create(self, user1, user2):

        thread = self.find(user1, user2)
        
        if thread is None:
            thread = Thread.objects.create()
            thread.users.add(user1, user2)

        return thread


class Thread(models.Model):
    users = models.ManyToManyField(User, related_name='threads')
    messages = models.ManyToManyField(Message)
    updated = models.DateTimeField(auto_now=True)

    objects = ThreadManager()

    class Meta:
        ordering = ['-updated']


    # Añadir aquí un campo updated, y luego una clase meta para indicar
    # que debe ser el campo por el que ordenar. Cada vez que se envíe un mensaje,
    # el campo updated debe actualizarse con la fecha y hora del mensaje.

    # En messages_changed, actualizaremos el campo updated cuando el action
    # sea 'post_add'


# Definimos una señal que será ejecutada siempre que haya un cambio en el campo
# Many-to-many "messages" de la clase Thread.
def messages_changed(sender, **kwargs):

    # El hilo que estamos viendo
    instance = kwargs.pop("instance", None) 

    # Un campo many to many, tiene varias acciones: pre_add y post_add.
    # Queremos actuar en el pre_add, para que no se agreguen mensajes de un usuario no pertenciente al hilo.
    action = kwargs.pop("action", None) 

    # El hilo puede tener varios mensajes dentro. Identificamos estos mensajes con su primary key.
    original_pk_set = kwargs.pop("pk_set", None) 
    
    # Guardaremos en este set los mensajes de los usuarios no pertenecientes al hilo.
    foreign_user_message_pk_set = set()

    if action == "pre_add":
        
        # Recorremos todos los mensajes del hilo.
        for msg_pk in original_pk_set:
            message = Message.objects.get(pk=msg_pk)
            
            # Comprobamos si el autor del mensaje pertenece al hilo.
            if message.user not in instance.users.all():
                # No pertenece, por lo que agregamos el mensaje al set de mensajes incorrectos.
                foreign_user_message_pk_set.add(msg_pk)

    # Si hay algun mensaje en foreign_user_message_pk_set, es eliminado del set original
    original_pk_set.difference_update(foreign_user_message_pk_set)
    instance.save()
                

# Con esta linea conectamos la señal "messages_changed" con el campo que queremos observar (campo
# "messages" de la clase Thread).
m2m_changed.connect(messages_changed, sender=Thread.messages.through)
