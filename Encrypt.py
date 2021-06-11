__all__ = ()

from cryptography.fernet import Fernet as FN
from socket import error, create_connection
from tkinter import messagebox
from functools import lru_cache
from operator import iadd

@lru_cache(typed=True)
class Internet:
    """Class for TCP connection with server

       here is also used encryption with symmetric key
    """

    __key_path = 'C:/PythonProgs/AIOServer/secret.key'

    # Function, to create connection with server
    def IntoNetwork(self, data, host='172.20.20.14', port=43333):
        try:
            # socket.create_connection returns link to socket object
            with create_connection((host, port)) as _sock:
                _sock.settimeout(3)
                __rst = self.ToConnect(_sock, data)
        except error as __err:
            messagebox.showinfo('Ошибка', __err)
        else:
            return __rst

    def ToConnect(self, sock, data):
        """Function, that encrypts message before sending,

           and (receiving/decoding) HEADER from server
           that contents the length of the incoming message
        """

        try:
            _recv_buffer = b''
            __query = self.encrypt_message(data)
            sock.sendall(__query)
            sock.send(b'^\n')
            while True:
                __msg = sock.recv(1024)
                if __msg: 
                    _recv_buffer = iadd(_recv_buffer, __msg)
                else: break
        except (UnicodeDecodeError, error,\
                ValueError, OSError, InterruptedError, Exception) as __err:
            messagebox.showinfo("Ошибка", __err)
        else:
            __ready = self.decrypt_message(_recv_buffer)
            if __ready: return __ready

    def decrypt_message(self, message, path=__key_path):
        try:
            with open(path, "rb") as __wr:
                __key = __wr.read()
                __f = FN(__key)
            __decrypted_message = __f.decrypt(message)
            __decoded_message = __decrypted_message.decode('utf8')
        except (OSError, Exception) as __err:
            messagebox.showinfo('Ошибка', __err)
        else:
            return __decoded_message

    def encrypt_message(self, message, path=__key_path):
        try:
            with open(path, "rb") as __wr:
                __key = __wr.read()
                __f = FN(__key)
            __encoded_message = message.encode('utf8')
            __encrypted_message = __f.encrypt(__encoded_message)
        except (OSError, Exception) as __err:
            messagebox.showinfo('Ошибка', __err)
        else:
            return __encrypted_message