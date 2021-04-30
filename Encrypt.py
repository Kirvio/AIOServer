__all__ = ()

from cryptography.fernet import Fernet as FN
from socket import AF_INET, socket, error, create_connection
from tkinter import messagebox
import time

class Internet:
    """Class for TCP connection with server

       here is also used encryption with symmetric key
    """

    __save_path='C:/ПО Заявки/Сервер Python/secret.key'

    # Function, to create connection to 
    # server with arguments, that defines the server
    def IntoNetwork(self, data, host='localhost', port=43333):
        try:
            # socket.create_connection returns link to socket object
            self._sock = create_connection((host, port))
            __rst = self.ToConnect(data)
            return __rst
        except error as __err:
            messagebox.showinfo('Ошибка', __err)

    def ToConnect(self, data):
        """Function, that encrypts message before sending,

           and (receiving/decoding) HEADER from server
           that contents the length of the incoming message
        """

        __HEADER = 64
        try:
            __query = self.encrypt_message(data)
            self._sock.sendall(__query)
            self._sock.send(b'^\n')
            while True:
                __msg_length = self._sock.recv(__HEADER).decode('utf8')
                __msg = self._sock.recv(int(__msg_length))
                if not __msg: break
                __ready = self.decrypt_message(__msg)
                if __ready: return __ready
        except (UnicodeDecodeError, error,\
                ValueError, OSError, InterruptedError) as __err:
            messagebox.showinfo("Ошибка", __err)
            return False

    def decrypt_message(self, message, path=__save_path):
        try:
            with open(path, "rb") as __wr:
                __key = __wr.read()
                __f = FN(__key)
            __decrypted_message = __f.decrypt(message)
            __decoded_message = __decrypted_message.decode('utf8')
            return __decoded_message
        except (OSError, Exception) as err:
            messagebox.showinfo('Ошибка', __err)

    def encrypt_message(self, message, path=__save_path):
        try:
            with open(path, "rb") as __wr:
                __key = __wr.read()
                __f = FN(__key)
            __encoded_message = message.encode('utf8')
            __encrypted_message = __f.encrypt(__encoded_message)
            return __encrypted_message
        except (OSError, Exception) as err:
            messagebox.showinfo('Ошибка', __err)