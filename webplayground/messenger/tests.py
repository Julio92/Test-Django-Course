from django.test import TestCase
from django.contrib.auth.models import User
from .models import Thread, Message


# Create your tests here.

    

class ThreadTestCase(TestCase):
    
    def setUp(self):

        # Given...:estos usuarios e hilo...
        self.user1 = User.objects.create_user('user1', None, 'test1234')
        self.user2 = User.objects.create_user('user2', None, 'test1234')    
        self.user3 = User.objects.create_user('user3', None, 'test1234')

        self.thread = Thread.objects.create()
    
    #Ojo!! Los métodos de pruebas deben empezar con "test".    
    # Comprueba que los usuarios son agregados al hilo correctamente.
    def test_add_users_to_thread(self):

        # When...: Añadimos los dos usuarios al hilo
        self.thread.users.add(self.user1, self.user2)

        # Then...: La cantidad de usuarios dentro del hilo debe ser 2
        self.assertEqual( len( self.thread.users.all() ), 2 )


    # Comprueba que se puede recuperar un hilo a partir del usuario.
    def test_filter_thread_by_users(self):

        # When...: Añadimos los dos usuarios al hilo ...
        self.thread.users.add(self.user1, self.user2)
        # ...Y filtramos sobre los hilos existentes, por estos usuarios a la vez...
        threads = Thread.objects.filter(users=self.user1).filter(users=self.user2)

        # Then...: El hilo que hemos creado en el set up, es el mismo hilo que recuperamos con el filtro.
        self.assertEqual(self.thread, threads[0])


    # Comprueba que se puede recuperar un mensaje a partir del usuario.
    def test_filter_non_existent_thread(self):

        # When...: filtramos sobre los hilos existentes, por usuarios que no están en ningún hilo
        threads = Thread.objects.filter(users=self.user1).filter(users=self.user2)

        # Then...: No deberíamos haber encontrado ningún hilo.
        self.assertEqual(len(threads), 0)


    # Comprueba que los mensajes se añaden al hilo correctamente.
    def test_add_messages_to_thread(self):

        # When...: Añadimos los dos usuarios al hilo ...
        self.thread.users.add(self.user1, self.user2)

        # ...Y escribimos dos mensajes dentro del hilo
        message1 = Message.objects.create(user=self.user1, content = "Hey!")
        message2 = Message.objects.create(user=self.user2, content = "What's up!")
        self.thread.messages.add(message1, message2)

        # Then...: El hilo debe tener 2 mensajes.
        self.assertEqual(len(self.thread.messages.all()), 2)


    # Comprueba que no se añaden mensajes al hilo de usuarios que no pertenecel al hilo.
    def test_add_message_from_user_not_in_thread(self):

        # When...: Añadimos dos usuarios al hilo ...
        self.thread.users.add(self.user1, self.user2)

        # ...Y escribimos dos mensajes dentro del hilo, y otro adicional de un usuario no perteneciente al hilo
        message1 = Message.objects.create(user=self.user1, content = "Hey!")
        message2 = Message.objects.create(user=self.user2, content = "What's up!")
        message3 = Message.objects.create(user=self.user3, content = "Oh shit!")

        self.thread.messages.add(message1, message2, message3)
        
        # Then...: El hilo debe tener 2 mensajes.
        self.assertEqual(len(self.thread.messages.all()), 2)


    # Comprueba que se puede recuperar un hilo usando el Model Manager.
    def test_find_thread_with_custom_manager(self):

        # When...: Añadimos los dos usuarios al hilo ...
        self.thread.users.add(self.user1, self.user2)
        # ...Y filtramos sobre los hilos existentes usando el Model Manager
        thread = Thread.objects.find(self.user1, self.user2)

        # Then...: El hilo que hemos creado en el set up, es el mismo hilo que recuperamos con el Model Manager.
        self.assertEqual(self.thread, thread)


    # Comprueba que se puede recuperar un hilo usando el Model Manager y, 
    # sino lo encuentra, crea uno nuevo.
    def test_find_or_create_thread_with_custom_manager(self):

        # When...: Añadimos los dos usuarios al hilo ...
        self.thread.users.add(self.user1, self.user2)
        # ...Y buscamos/creamos sobre los hilos existentes usando el Model Manager
        thread = Thread.objects.find_or_create(self.user1, self.user2)
        # Then...: El hilo que hemos creado en el set up, es el mismo hilo que recuperamos con el Model Manager.
        self.assertEqual(self.thread, thread)

        # When...: Y si ademas, buscamos/creamos sobre los hilos existentes, con un usuario que no tiene ningun hilo
        thread = Thread.objects.find_or_create(self.user1, self.user3)
        # Then...: El hilo que recuperamos, debe ser distinto a None.
        self.assertIsNotNone(thread)