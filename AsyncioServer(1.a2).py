from aiosqlite import connect, DatabaseError
import asyncio
import sys
import socket
import logging
import atexit
from AIOEncryption import decrypt_message, encrypt_message, check_pass, to_hash_password

# Настроить логгирование

class MyServer(object):
    __HEADER = 64

    def __init__(self):

        self.server = None # encapsulates the server sockets
        self.log = logging.getLogger(__name__)
        """
        f_format = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.log.setLevel(logging.INFO)
        f_handler = logging.FileHandler('ServerLog.log')
        f_handler.setLevel(logging.INFO)
        f_handler.setFormatter(f_format)
        self.log.addHandler(f_handler)
        """
        # this keeps track of all the clients that connected to our
        # server.  It can be useful in some cases, for instance to
        # kill client connections or to broadcast some data to all
        # clients...

        self.clients = {} # task -> (reader, writer)

    # Корутина, осуществляющая доступ к БД
    async def __access_db(self, SQLdiction=tuple()):
        try:
            __db = await connect("address_book.db")
        except DatabaseError as __MSG:
            return __MSG
        else:
            if SQLdiction[0] == "ENTER":
                try:
                    __Log, __Passs = SQLdiction[1], SQLdiction[2]
                    __cursor = await __db.execute("SELECT IIF(Login = :Login, (SELECT Password FROM Cipher), 'NOLOG'), IIF(Login = :Login, \
                    (SELECT employee_FIO FROM Cipher), 'NOLOG') FROM Cipher", {'Login': __Log }) 
                    __msg = await __cursor.fetchall()
                    for __i in __msg:
                        if __i[0] == "NOLOG": 
                            print("Попытка входа с неправильным логином")
                            return __i[0]
                        else:
                            if (await check_pass(__Passs, __i[0])):
                                print("Выполнен запрос на вход в программу")
                                __msg = "^".join(["GO", __i[1]])
                                return __msg
                            else:
                                __msg = "Fail"
                                print("Попытка входа с неправильным паролем")
                                return __msg
                except DatabaseError as __MSG:
                    self.log.error("Exception occurred", exc_info=True)
                finally:      
                    await __db.close()
            elif SQLdiction[0] == "REGISTER":
                try:
                    __new_hash = (await to_hash_password(SQLdiction[3]))
                    print(__new_hash)
                    __cursor = await __db.execute("INSERT INTO Cipher (ID, Login, Password, employee_FIO)\
                        VALUES (:ID, :Login, :Password, :employee_FIO)", 
                        {'ID': SQLdiction[1], 'Login': SQLdiction[2], 'Password':__new_hash, 'employee_FIO': SQLdiction[4]})           
                    await __db.commit()
                    __msg = 'Reg'
                    print("Пользователь зарегистрирован")
                    return __msg
                except DatabaseError as __MSG:
                    self.log.error("Exception occurred", exc_info=True)
                finally:
                    await __db.close()
            elif SQLdiction[0] == "DELETEUSER":
                try:
                    await __db.execute("DELETE FROM Cipher WHERE ID = :ID", {'ID': SQLdiction[1]})
                    await __db.commit()
                    __msg = "Пользователь удален"
                    print("Выполнен запрос на удаление пользователя")
                    return __msg
                except DatabaseError as __MSG:
                    self.log.error("Exception occurred", exc_info=True)
                finally:
                    await __db.close()
            elif SQLdiction[0] == "ALLQUERY":
                try:
                    __cursor = await __db.execute("SELECT RecDate, FIO, address, telephone, reason, information, for_master, master, record_value, Category, FIO_employee, RegDate \
                    FROM records")  # ALTER TABLE records ADD category text, ADD employee_FIO text, ADD Reg_Time DATETIME
                    __records = await __cursor.fetchall()
                    __print_records = ''
                    for __record in __records:
                        __print_records += '^'.join([str(__record[0]),str(__record[1]),str(__record[2]),str(__record[3]),str(__record[4]),\
                        str(__record[5]),str(__record[6]),str(__record[7]),str(__record[8]),str(__record[9]),str(__record[10]),str(__record[11]),'#'])
                    print("Выполнен запрос на заявки")
                    return __print_records
                except DatabaseError as __MSG:
                    self.log.error("Exception occurred", exc_info=True)
                finally:
                    await __db.close()
            elif SQLdiction[0] == "USERQUERY":
                try:
                    __cursor = await __db.execute("SELECT ID, Login, Password, employee_FIO FROM Cipher")
                    __records = await __cursor.fetchall()
                    __print_logins = ''
                    for __record in __records:
                        __print_logins += '^'.join([str(__record[0]), str(__record[1]), str(__record[2]), str(__record[3]), '#'])
                    print("Выполнен запрос на логин-пароль")
                    return __print_logins
                except DatabaseError as __MSG:
                    self.log.error("Exception occurred", exc_info=True)
                finally:
                    await __db.close()
            elif SQLdiction[0] == "CURQUERY":
                try:
                    __cursor = await __db.execute("SELECT RecDate, FIO, address, telephone, reason, information, for_master, master, record_value, Category, FIO_employee, RegDate \
                    FROM records WHERE RecDate = :RecDate", { 'RecDate': SQLdiction[1]})  # ALTER TABLE records ADD category text, ADD employee_FIO text, ADD Reg_Time DATETIME
                    __records = await __cursor.fetchall()   
                    if __records == []:
                        print("На текущий день ничего нет")
                        __msg = "No"
                        return __msg
                    else:
                        __print_records = ''
                        for __record in __records:
                            __print_records += '^'.join((str(__record[0]),str(__record[1]),str(__record[2]),str(__record[3]),str(__record[4]),\
                            str(__record[5]),str(__record[6]),str(__record[7]),str(__record[8]),str(__record[9]),str(__record[10]),str(__record[11]),'#'))
                            print("Выполнен запрос на текущие заявки")
                            return __print_records
                except DatabaseError as __MSG:
                    self.log.error("Exception occurred", exc_info=True)
                finally:
                    await __db.close()
            elif SQLdiction[0] == "INSERT":              
                try:
                    await __db.execute("INSERT INTO records (FIO, address, telephone, reason, information, for_master, master, record_value, Category, FIO_employee, RegDate, RecDate) \
                    VALUES (:FIO, :address, :telephone, :reason, :information, :for_master, :master, :record_value, :Category, :FIO_employee, :RegDate, :RecDate)",
                        {
                            'FIO': SQLdiction[1],
                            'address': SQLdiction[2],
                            'telephone': SQLdiction[3],
                            'reason': SQLdiction[4],
                            'information': SQLdiction[5],
                            'for_master': SQLdiction[6],
                            'master': SQLdiction[7],
                            'record_value': SQLdiction[8],
                            'Category': SQLdiction[9],
                            'FIO_employee': SQLdiction[10],
                            'RegDate': SQLdiction[11],
                            'RecDate': SQLdiction[12]
                        })
                    await __db.commit()                         
                    __msg = "Новая запись добавлена"
                    print(__msg)
                    return __msg
                except DatabaseError as __MSG:
                    self.log.error("Exception occurred", exc_info=True)
                finally:
                    await __db.close()
            elif SQLdiction[0] == "DELETE":
                try:
                    __cursor = await __db.execute("DELETE FROM records\
                    WHERE address = :address AND record_value = 'Закрыта'", {'address': SQLdiction[1]})
                    __msg = await __cursor.fetchall()
                    await __db.commit()               
                    if __msg:                   
                        return __msg
                except DatabaseError as __MSG:
                    self.log.error("Exception occurred", exc_info=True)
                finally:
                    await __db.close()
            elif SQLdiction[0] == "UPDATE":
                try: 
                    await __db.execute("UPDATE records \
                    SET FIO = :FIO, address = :address, telephone = :telephone, reason = :reason, information = :information, for_master = :for_master, master = :master,\
                    record_value = :record_value, Category = :Category, RecDate = :RecDate\
                    WHERE address = :address",
                        {  
                            'FIO': SQLdiction[1], 
                            'address': SQLdiction[2], 
                            'telephone': SQLdiction[3], 
                            'reason': SQLdiction[4], 
                            'information': SQLdiction[5],
                            'for_master': SQLdiction[6], 
                            'master': SQLdiction[7], 
                            'record_value': SQLdiction[8],
                            'Category': SQLdiction[9],
                            'RecDate': SQLdiction[10]
                        })
                    await __db.commit()       
                    __msg = "Запись обновлена"
                    print(__msg)
                    return __msg
                except DatabaseError as __MSG:          
                    self.log.error("Exception occurred", exc_info=True)
                finally:
                    await __db.close() 
            else:
                __MSG = "Неправильный запрос"
                return __MSG

    async def __accept_client(self, client_reader, client_writer):

        """
        This method accepts a new client connection and creates a Task
        to handle this client.  self.clients is updated to keep track
        of the new client.
        """

        task = await asyncio.wait_for(self.__handle_client(client_reader, client_writer), 20)
        self.clients[task] = (client_reader, client_writer)

        async def __client_done(task):
            del self.clients[task]
            self.log.info("Client task done")
            print('client task done', file = sys.stderr)
        await __client_done(task)

    async def __handle_client(self, client_reader, client_writer):
        __request = await self.__read_request(client_reader)
        if __request:
            __incoming = await self.__access_db(SQLdiction = __request) 
            await self.__write_response(client_writer, __incoming)
            client_writer.close()
            await client_writer.wait_closed()
            return

    async def __read_request(self, reader):
        try:
            line = await reader.readuntil(separator=b'\x00')
            if line:
                line = await decrypt_message(line)
                line = line.split("^")
                return line
        except (asyncio.LimitOverrunError, asyncio.IncompleteReadError) as err:
            self.log.error("Exception occurred", exc_info=True)
            print(err)

    async def __write_response(self, writer, IncData):
        try:
            addr = writer.get_extra_info('peername')
        except (OSError, ConnectionResetError, Exception) as __err:
            self.log.error("Exception occurred", exc_info=True)
        else:
            self.log.info(f"Connection accepted from {addr!r}")
            print(f"Received query from {addr!r}")
            try:
                __query = await encrypt_message(IncData)
                __query_length = len(__query)
                __send_length = str(__query_length).encode('utf8')
                __send_length += b' ' * (self.__HEADER - len(__send_length))
                try:
                    writer.write(__send_length)
                    writer.write(__query)
                    await writer.drain()
                except (OSError, ConnectionResetError, Exception) as __err:
                    print(__err)
            except (OSError, ConnectionResetError, Exception) as __err:
                print(__err)

    async def start(self):

        """
        Starts the TCP server, so that it listens on port 43333.
        For each client that connects, the accept_client method gets
        called. This method runs the loop until the server sockets
        are ready to accept connections.
        """

        self.server = await asyncio.start_server(self.__accept_client, 'localhost', 43333, family = socket.AF_INET, backlog = 20, reuse_address = True)
        addr = self.server.sockets[0].getsockname()
        self.log.info(f'Serving on {addr}')
        print(f'Serving on {addr}')

        async with self.server:
            await self.server.serve_forever()

    async def stop(self):

        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
            self.server = None

if __name__ == "__main__":
    log = logging.getLogger('')
    f_format = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log.setLevel(logging.INFO)
    f_handler = logging.FileHandler('ServerLog.log')
    f_handler.setLevel(logging.INFO)
    f_handler.setFormatter(f_format)
    log.addHandler(f_handler)
    MServer = MyServer()
    asyncio.run(MServer.start())
    __loop = asyncio.get_running_loop()
    __loop.set_debug(True)
    if __loop.get_debug():
        log.debug("%r resumes writing", self)
    atexit.register(MServer.stop())
