from cryptography.fernet import Fernet as FN

"""
Модуль шифрования для клиентской программы
"""

__save_path = 'C:/ПО Заявки/Сервер Python/secret.key'
    
# Функция расшифровывает данные
def decrypt_message(message):
    try:
        with open(__save_path, "rb") as __wr:
            __key = __wr.read()
            __f = FN(__key)
        __decrypted_message = __f.decrypt(message)                
        __decoded_message = __decrypted_message.decode('utf8')
        return __decoded_message
    except (OSError, Exception) as err:
        pass

# Функция зашифровывает данные
def encrypt_message(message):
    try:
        with open(__save_path, "rb") as __wr:
            __key = __wr.read()
            __f = FN(__key)
        __encoded_message = str(message).encode('utf8')
        __encrypted_message = __f.encrypt(__encoded_message)
        return __encrypted_message
    except (OSError, Exception) as err:
        pass