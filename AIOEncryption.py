from bcrypt import checkpw, hashpw, gensalt
from cryptography.fernet import Fernet as FN
import asyncio

__save_path = 'C:/ПО Заявки/Сервер Python/secret.key'

# Asyncio decorator that returns Future while running task in background thread (good for cpu bound functions that release the GIL such as `bcrypt.checkpw`) 
def asyncify(func):        
    #  * - распаковывает обьекты, внутри которых находятся некоторые элементы(в данном случае аргументы функции)
    async def inner(*args, **kwargs):
        __loop = asyncio.get_running_loop()
        __func_out = await __loop.run_in_executor(None, func, *args, **kwargs)
        return __func_out
    return inner

# Расшифровка данных при получении
@asyncify 
def decrypt_message(message):
    try:
        with open(__save_path, "rb") as __wr:
            __key = __wr.read()
            __f = FN(__key)
        __decrypted_message = __f.decrypt(message)                
        __decoded_message = __decrypted_message.decode('utf8')
        return __decoded_message
    except (OSError, Exception) as err:
        print(err)

# Шифрование данных перед отправкой
@asyncify
def encrypt_message(message):  
    try:
        with open(__save_path, "rb") as __wr:
            __key = __wr.read()
            __f = FN(__key)
        __encoded_message = str(message).encode('utf8')
        __encrypted_message = __f.encrypt(__encoded_message)
        return __encrypted_message
    except (OSError, Exception) as err:
        print(err)

# Проверка хэша пароля                
@asyncify
def check_pass(password, hashed_pass):
    return checkpw(password.encode('utf8'), hashed_pass)

# Хэширование пароля
@asyncify
def to_hash_password(get_password):
    return hashpw(get_password.encode('utf8'), gensalt(12))