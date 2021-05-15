__all__ = ()

from cryptography.fernet import Fernet as FN
from socket import error, create_connection
from tkinter import messagebox

class Internet:
    """Class for TCP connection with server

       here is also used encryption with symmetric key
    """

    __key_path = 'C:/PythonProgs/AIOServer/secret.key'

    # Function, to create connection to
    # server with arguments, that defines the server
    def IntoNetwork(self, data, host='172.20.20.14', port=43333):
        try:
            # socket.create_connection returns link to socket object
            self._sock = create_connection((host, port))
            __rst = self.ToConnect(data)
        except error as __err:
            messagebox.showinfo('Ошибка', __err)
        else:
            return __rst

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