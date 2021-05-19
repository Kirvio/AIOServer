__all__ = ()

from bcrypt import checkpw, hashpw, gensalt
from cryptography.fernet import Fernet as FN
import asyncio

class AsyncioBlockingIO:
    """Class, that contents operations with blocking I/O(CPU bound).

       To prevent blocking in event loop,
       use asyncify decorator,
       that runs CPU bound function in executor
       В этом классе содержатся операции блокирующие
       I/O(CPU bound), что-бы не допустить блока
       используется декоратор asyncify
       это функция запускает операции в отдельном потоке
       метод .run_in_executor
    """

    # Path to key for encryption and decryption
    key_path = 'C:/PythonProgs/AIOServer/secret.key'

    # Asyncio decorator that returns Future
    # while running task in background thread
    # (good for cpu bound functions that release the GIL such as `bcrypt.checkpw`)
    def asyncify(func):
        async def inner(*args, **kwargs):
            loop = asyncio.get_running_loop()
            func_out = await loop.run_in_executor(None, func, *args, **kwargs)
            return func_out
        return inner

    @asyncify
    def decrypt_message(self, message, path = key_path):
        try:
            with open(path, "rb") as wr:
                key = wr.read()
                f = FN(key)
            decrypted_message = f.decrypt(message)
            decoded_message = decrypted_message.decode('utf8')
        except (OSError, Exception):
            raise
        else:
            return decoded_message

    @asyncify
    def encrypt_message(self, message, path = key_path):
        try:
            with open(path, "rb") as wr:
                key = wr.read()
                f = FN(key)
            encoded_message = str(message).encode('utf8')
            encrypted_message = f.encrypt(encoded_message)
        except (OSError, Exception):
            raise
        else:
            return encrypted_message

    @asyncify
    def check_pass(self, password, hashed_pass):
        return checkpw(password.encode('utf8'), hashed_pass)

    @asyncify
    def to_hash_password(self, get_password):
        return hashpw(get_password.encode('utf8'), gensalt(12))