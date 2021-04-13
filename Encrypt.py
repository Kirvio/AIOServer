from cryptography.fernet import Fernet as FN
from socket import AF_INET, socket, error, create_connection
from tkinter import messagebox
import time

"""
Модуль для подключения к серверу по протоколу TCP 
здесь же реализовано шифрование с симметричным ключем
"""

class Internet:
    __save_path = 'C:/ПО Заявки/Сервер Python/secret.key'
    def IntoNetwork(self, data, host = 'localhost', port = 43333, sock = None):
        if sock is None:
            try:
                # create_connection возвращает ссылку на существующий сокет для подключения
                self._sock = create_connection((host, port))
            except error as __err:
                messagebox.showinfo('Ошибка', __err)
            else:
                try:
                    __rst = self.ToConnect(data)
                    return __rst
                except error as err:
                    print(err)
        else:
            self._sock = sock
            try:
                __rst = self.ToConnect(data)
                return __rst
            except error as err:
                print(err)

    def ToConnect(self, data):
        __HEADER = 64
        try:
            __query = self.encrypt_message(data)
            self._sock.sendall(__query)
            self._sock.send(b'^\x00')
            while True:
                __msg_length = self._sock.recv(__HEADER).decode('utf8')
                __msg = self._sock.recv(int(__msg_length))
                if not __msg:
                    break
                __ready = self.decrypt_message(__msg)
                return __ready
        except (UnicodeDecodeError, error, ValueError, OSError, InterruptedError) as __err:
            messagebox.showinfo("Ошибка", __err)
            return False
        finally:
            self._sock.close()

    def decrypt_message(self, message, path = __save_path):
        try:
            with open(path, "rb") as __wr:
                __key = __wr.read()
                __f = FN(__key)
            __decrypted_message = __f.decrypt(message)                
            __decoded_message = __decrypted_message.decode('utf8')
            return __decoded_message
        except (OSError, Exception) as err:
            return err

    def encrypt_message(self, message, path = __save_path):
        try:
            with open(path, "rb") as __wr:
                __key = __wr.read()
                __f = FN(__key)
            __encoded_message = message.encode('utf8')
            __encrypted_message = __f.encrypt(__encoded_message)
            return __encrypted_message
        except (OSError, Exception) as err:
            print(err)
            return err

"""
# Функция расшифровывает данные
    def IntoNetwork(self, data = str(), host = 'localhost', port = 43333):
        self.__sock = None
        if self.__sock == None:
            try:
                self.__sock = create_connection((host, port))
            except error as __err:
                messagebox.showinfo('Ошибка', __err)
            else:
                try:
                    __rst = self.ToConnect(data = data)
                    return __rst
                except error as err:
                    print(err)
        else:
            if data == 'end':
                self.__sock.close()
            else:
                try:
                    __rst = self.ToConnect(data = data)
                    return __rst
                except error as err:
                    print(err)
# asyncio client
async def IntoNetwork(self, data, sock):
    self.sock = sock
        if self.sock == None:
            try:
                self.sock = await asyncio.open_connection('localhost', 43333, family = socket.AF_INET)
                reader, writer = self.sock
            except Exception as __err:
                print(__err)
            else:
                try:
                    __rst = await self.WR(data, reader, writer)
                    return __rst
                except Exception as err:
                    print(err)
        else:
            reader, writer = self.sock
            try:
                __rst = await self.WR(data, reader, writer)
                return __rst
            except Exception as err:
                print(err)

async def WR(self, data, reader, writer):
    try:
        writer.write(data.encode('utf8'))
        writer.write(b'^\x00')
        await writer.drain()
        try:
            line = await reader.readuntil(separator=b'\x00')
            line = line.decode('utf8')
            return line
        except asyncio.LimitOverrunError as err:
            print(err)
        finally:
            writer.close()
            await writer.wait_closed()
    except (UnicodeDecodeError, ValueError, OSError, InterruptedError, Exception) as __err:
        messagebox.showinfo("Ошибка", __err)
        return False

def Main(data):
try:
    rrr = asyncio.run(Internet().IntoNetwork(data))
    return rrr
except Exception as exc:
    print(exc)
"""