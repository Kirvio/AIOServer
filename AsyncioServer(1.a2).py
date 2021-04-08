from aiosqlite import connect, DatabaseError
import asyncio
import sys
from AIOEncryption import decrypt_message, encrypt_message, check_pass, to_hash_password

class MyServer(object):

    __HEADER = 64

    def __init__(self):

        self.server = None # encapsulates the server sockets

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
                                __msge = "^".join(["GO", __i[1]])
                                return __msge
                            else:
                                __msge = "Fail"
                                print("Попытка входа с неправильным паролем")
                                return __msge
                except DatabaseError as __MSG:
                    print(__MSG)
                    return __MSG
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
                    print(__MSG)
                    return __MSG
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
                    print(__MSG)
                    return __MSG
                finally:
                    await __db.close()
            elif SQLdiction[0] == "ALLQUERY":
                try:
                    __cursor = await __db.execute("SELECT RecDate, FIO, address, telephone, reason, information, for_master, master, record_value, Category, FIO_employee, RegDate \
                    FROM records")  # ALTER TABLE records ADD category text, ADD employee_FIO text, ADD Reg_Time DATETIME
                    __records = await __cursor.fetchall()
                    __print_records = ''
                    for __record in __records:
                        __print_records += '^'.join((str(__record[0]),str(__record[1]),str(__record[2]),str(__record[3]),str(__record[4]),\
                        str(__record[5]),str(__record[6]),str(__record[7]),str(__record[8]),str(__record[9]),str(__record[10]),str(__record[11]),'#'))
                    print("Выполнен запрос на заявки")
                    return __print_records
                except DatabaseError as __MSG:
                    return __MSG
                finally:
                    await __db.close()
            elif SQLdiction[0] == "USERQUERY":
                try:
                    __cursor = await __db.execute("SELECT ID, Login, Password, employee_FIO\
                    FROM Cipher")
                    __records = await __cursor.fetchall()
                    __print_logins = ''
                    for __record in __records:
                        __print_logins += '^'.join((str(__record[0]), str(__record[1]), str(__record[2]), str(__record[3]), '#'))
                    print("Выполнен запрос на логин-пароль")
                    return __print_logins
                except DatabaseError as __MSG:
                    return __MSG
                finally:
                    await __db.close()
            elif SQLdiction[0] == "CURQUERY":
                try:
                    __cursor = await __db.execute("SELECT RecDate, FIO, address, telephone, reason, information, for_master, master, record_value, Category, FIO_employee, RegDate \
                    FROM records WHERE RecDate = :RecDate", { 'RecDate': SQLdiction[1]})  # ALTER TABLE records ADD category text, ADD employee_FIO text, ADD Reg_Time DATETIME
                    __records = await __cursor.fetchall()        
                    __print_records = ''
                    for __record in __records:
                        if __record[0] == 'None':
                            print("На текущий день ничего нет")
                            __msg = __record[0]
                            return __msg
                        else:
                            __print_records += '^'.join((str(__record[0]),str(__record[1]),str(__record[2]),str(__record[3]),str(__record[4]),\
                            str(__record[5]),str(__record[6]),str(__record[7]),str(__record[8]),str(__record[9]),str(__record[10]),str(__record[11]),'#'))
                            print("Выполнен запрос на текущие заявки")
                            return __print_records
                except DatabaseError as __MSG:
                    print(__MSG)
                    return __MSG
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
                    print(__MSG)
                    return __MSG
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
                    return __MSG
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
                    print(__MSG)
                    return __MSG
                finally:
                    await __db.close() 
            else:
                __MSG = "Неправильный запрос"
                return __MSG

    async def accept_client(self, client_reader, client_writer):

        """
        This method accepts a new client connection and creates a Task
        to handle this client.  self.clients is updated to keep track
        of the new client.
        """

        # start a new Task to handle this specific client connection
        task = await asyncio.create_task(self.__handle_client(client_reader, client_writer))
        self.clients[task] = (client_reader, client_writer)
        def __client_done(task):
                del self.clients[task]
                print('client task done:', task, file = sys.stderr)
        __client_done(task)

    async def __handle_client(self, client_reader, client_writer):
        __request = await self.__read_request(client_reader)
        __response = await self.__handle(__request)    
        __incoming = await self.__access_db(SQLdiction = __response) 
        __answer = await self.__handle(__incoming)
        await self.__write_response(client_writer, __answer)
        __signal = 'client served'
        return __signal

    # Корутина, читающая запрос
    async def __read_request(self, reader):
        while True:
            try:
                __msg_length = (await reader.read(self.__HEADER)).decode('utf8') 
                if not __msg_length:
                    break     
                __msg_length = int(__msg_length)
                __request = (await reader.read(__msg_length))
                if not __request:
                    break     
                __response = (await decrypt_message(__request))
                __response = __response.split("^")
            except (UnicodeDecodeError, Exception, ValueError, OSError) as __err:           
                print(__err)           
            finally:
                return __response

    # Корутина, пишущая ответ
    async def __write_response(self, writer, IncData=()):
        __query = (await encrypt_message(IncData))
        __query_length = len(__query)
        __send_length = str(__query_length).encode('utf8')
        __send_length += b' ' * (self.__HEADER - len(__send_length))
        try:
            
            # Посылает длину и сам запрос
            writer.write(__send_length)
            writer.write(__query)
            await writer.drain()
        except (OSError, ConnectionResetError, Exception) as __err:
            print(__err)
        finally:
            writer.close()
            await writer.wait_closed()

    async def start(self):

        """
        Starts the TCP server, so that it listens on port 43333.
        For each client that connects, the accept_client method gets
        called. This method runs the loop until the server sockets
        are ready to accept connections.
        """

        self.server = await asyncio.start_server(self.accept_client, 'localhost', 43333)

        async with self.server:
            await self.server.serve_forever()

    async def stop(self):

        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
            self.server = None

    # Корутина, удерживающая запрос
    async def __handle(self, request):
        await asyncio.sleep(0.5)
        return request

# Запуск программы
if __name__ == "__main__": 
    MServer = MyServer()
    try:
        asyncio.run(MServer.start())
        __loop = asyncio.get_running_loop()
        __loop.call_later(1, MServer.accept_client, __loop)
        __loop.set_debug(True)
        __loop.get_debug()
    finally:
        MServer.stop()