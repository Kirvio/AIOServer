from aiosqlite import connect, DatabaseError
import asyncio
import sys
from AIOEncryption import decrypt_message, encrypt_message, check_pass, to_hash_password

class MyServer(object):

    __HEADER = 64

    def __init__(self):

        self.__server = None # encapsulates the server sockets

        # this keeps track of all the clients that connected to our
        # server.  It can be useful in some cases, for instance to
        # kill client connections or to broadcast some data to all
        # clients...

        self.__clients = {} # task -> (reader, writer)

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
                                print("Вход в программу выполнен")
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
                    __cursor = await __db.execute("INSERT INTO Cipher (id, Login, Password, employee_FIO)\
                        VALUES (:id, :Login, :Password, :employee_FIO) \
                        WHERE NOT EXISTS (SELECT id FROM Cipher WHERE id = :id)", 
                        {'id': SQLdiction[1], 'Login': SQLdiction[2], 'Password':__new_hash, 'employee_FIO': SQLdiction[4]})
                    __msg = await __cursor.fetchone()
                    print(__msg)
                    if __msg[0] == 'EX':
                        print(__msg)
                        return __msg
                    else:
                        await __db.commit()
                        __msg = 'Reg'
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
                    print(__msg)
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
                        __print_records += '^'.join([str(__record[0]),str(__record[1]),str(__record[2]),str(__record[3]),str(__record[4]),\
                        str(__record[5]),str(__record[6]),str(__record[7]),str(__record[8]),str(__record[9]),str(__record[10]),str(__record[11]),'#'])
                    print("Входящий запрос обработан")
                    return __print_records
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
                            __print_records += '^'.join([str(__record[0]),str(__record[1]),str(__record[2]),str(__record[3]),str(__record[4]),\
                            str(__record[5]),str(__record[6]),str(__record[7]),str(__record[8]),str(__record[9]),str(__record[10]),str(__record[11]),'#'])
                            print("Входящий запрос обработан")
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
                    __cursor = await __db.execute("DELETE FROM records WHERE address = :address AND record_value = 'Закрыта'", {'address': SQLdiction[1]})
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
                    await __db.execute("UPDATE records SET FIO = :FIO, address = :address, telephone = :telephone, reason = :reason, information = :information, for_master = :for_master, master = :master,\
                    record_value = :record_value, Category = :Category, RecDate = :RecDate WHERE address = :address",
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

    async def __accept_client(self, client_reader, client_writer):

        """
        This method accepts a new client connection and creates a Task
        to handle this client.  self.clients is updated to keep track
        of the new client.
        """

        # start a new Task to handle this specific client connection
        __task = await asyncio.create_task(self.__handle_client(client_reader, client_writer))
        self.__clients[__task] = (client_reader, client_writer)
        def __client_done(task):
                del self.__clients[__task]
                print('client task done:', __task, file = sys.stderr)
        __client_done(__task)

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
        try:
            __msg_length = (await reader.read(self.__HEADER)).decode('utf8')        
            __msg_length = int(__msg_length)
            __request = (await reader.read(__msg_length))
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

    def start(self, loop):

        """
        Starts the TCP server, so that it listens on port 43333.
        For each client that connects, the accept_client method gets
        called. This method runs the loop until the server sockets
        are ready to accept connections.
        """

        self.__server = loop.run_until_complete(
                    asyncio.start_server(self.__accept_client,
                                        'localhost', 43333,
                                        loop = loop))

    def stop(self, loop):

        """
        Stops the TCP server, i.e. closes the listening socket(s).
        This method runs the loop until the server sockets are closed.
        """

        if self.__server is not None:
            self.__server.close()
            loop.run_until_complete(self.__server.wait_closed())
            self.__server = None

    # Корутина, удерживающая запрос
    async def __handle(self, request):
        await asyncio.sleep(0.5)
        return request

def main():
    try:
        __loop = asyncio.get_event_loop()
        __loop.set_debug(True)

        # creates a server and starts listening to TCP connections
        __server = MyServer()
        __server.start(__loop)
        __loop.run_forever()
        __loop.get_debug()
    finally:
        __server.stop(__loop)
        __loop.close()

# Запуск программы
if __name__ == "__main__": 
    main()