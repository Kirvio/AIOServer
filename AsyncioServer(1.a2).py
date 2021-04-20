from aiosqlite import connect, DatabaseError
import asyncio
import sys
import socket
import logging
import aiolog
from AIOEncryption import AsyncioBlockingIO

"""
EAFP(Easier to ask for forgiveness then permission) code style
"""

class MyServer:
    __HEADER = 64

    def __init__(self):

        self.log = logging.getLogger(__name__)

        self.clients = {} 

    async def __enter(self, SQLlist=tuple()):
        async with connect("address_book.db") as __db:
            try:
                __Log, __Passs = SQLlist[1], SQLlist[2]
                __cursor = await __db.execute("SELECT IIF(Login = :Login, (SELECT Password FROM Cipher), 'NOLOG'), IIF(Login = :Login, \
                (SELECT employee_FIO FROM Cipher), 'NOLOG') FROM Cipher", {'Login': __Log }) 
                __msg = await __cursor.fetchall()
                for __i in __msg:
                    if __i[0] == "NOLOG":
                        self.log.info("Попытка входа с неправильным логином")
                        return __i[0]
                    else:
                        if (await AsyncioBlockingIO().check_pass(__Passs, __i[0])):
                            self.log.info(f"Сотрудник {__Log!r} авторизировался")
                            __msg = "^".join(["GO", __i[1]])
                            return __msg
                        else:
                            __msg = "Fail"
                            self.log.info("Попытка входа с неправильным логином")
                            return __msg
            except (DatabaseError, IndexError):
                self.log.error("Exception occurred", exc_info=True)
                raise

    async def __register(self, SQLlist=tuple()):
        async with connect("address_book.db") as __db:
            try:
                __id, __login, __password, __fio = SQLlist[1], SQLlist[2], SQLlist[3], SQLlist[4]
                __new_hash = (await AsyncioBlockingIO().to_hash_password(__password))
                __cursor = await __db.execute("INSERT INTO Cipher (ID, Login, Password, employee_FIO)\
                    VALUES (:ID, :Login, :Password, :employee_FIO)", 
                    {'ID': __id, 'Login': __login, 'Password':__new_hash, 'employee_FIO': __fio})           
                await __db.commit()
                __msg = 'Reg'
                return __msg
            except (DatabaseError, IndexError):
                self.log.error("Exception occurred", exc_info=True)
                raise
            finally:
                self.log.info(f"Сотрудник {__fio!r} зарегистрирован")

    async def __deleteuser(self, SQLlist=tuple()):
        async with connect("address_book.db") as __db:
            try:
                __id = SQLlist[1]
                await __db.execute("DELETE FROM Cipher WHERE ID = :ID", {'ID': __id})
                await __db.commit()
                __msg = "Пользователь удален"
                return __msg
            except (DatabaseError, IndexError):
                self.log.error("Exception occurred", exc_info=True)
                raise
            finally:
                self.log.info(f"Сотрудник {__id!r} удален из БД")

    async def __allquery(self):
        async with connect("address_book.db") as __db:
            try:
                __cursor = await __db.execute("SELECT RecDate, FIO, address, telephone, reason, information, for_master, master, record_value, Category, FIO_employee, RegDate \
                FROM records")
                __records = await __cursor.fetchall()
                __print_records = ''
                for __record in __records:
                    __print_records += '^'.join((str(__record[0]),str(__record[1]),str(__record[2]),str(__record[3]),str(__record[4]),\
                    str(__record[5]),str(__record[6]),str(__record[7]),str(__record[8]),str(__record[9]),str(__record[10]),str(__record[11]),'#'))
                return __print_records
            except (DatabaseError, IndexError):
                self.log.error("Exception occurred", exc_info=True)
                raise
            finally:
                self.log.info(f"Запрос на все заявки")
    
    async def __userquery(self):
        async with connect("address_book.db") as __db:
            try:
                __cursor = await __db.execute("SELECT ID, Login, Password, employee_FIO FROM Cipher")
                __records = await __cursor.fetchall()
                __print_logins = ''
                for __record in __records:
                    __print_logins += '^'.join((str(__record[0]), str(__record[1]), str(__record[2]), str(__record[3]), '#'))
                return __print_logins
            except (DatabaseError, IndexError):
                self.log.error("Exception occurred", exc_info=True)
                raise
            finally:
                self.log.info(f"Запрос на информацию о сотрудниках")

    async def __curquery(self, SQLlist=tuple()):
        async with connect("address_book.db") as __db:
            try:
                __recdate = SQLlist[1]
                __cursor = await __db.execute("SELECT RecDate, FIO, address, telephone, reason, information, for_master, master, record_value, Category, FIO_employee, RegDate \
                FROM records WHERE RecDate = :RecDate", { 'RecDate': __recdate})  # ALTER TABLE records ADD category text, ADD employee_FIO text, ADD Reg_Time DATETIME
                __records = await __cursor.fetchall()
                if __records == None:
                    print("На текущий день ничего нет")
                    __msg = "No"
                    return __msg
                else:
                    __print_records = ''
                    for __record in __records:
                        __print_records += '^'.join((str(__record[0]),str(__record[1]),str(__record[2]),str(__record[3]),str(__record[4]),
                        str(__record[5]),str(__record[6]),str(__record[7]),str(__record[8]),str(__record[9]),str(__record[10]),str(__record[11]),'#'))
                        return __print_records
            except (DatabaseError, IndexError):
                self.log.error("Exception occurred", exc_info=True)
                raise
            finally:
                self.log.info(f"Запрос на текущие заявки")

    async def __insert(self, SQLlist=tuple()):
        async with connect("address_book.db") as __db:
            try:
                __fio, __address, __telephone, __reason, __information, __for_master,\
                __master, __record_value, __category, __fio_employee, __regdate, __recdate = SQLlist[1], SQLlist[2], SQLlist[3],\
                SQLlist[4], SQLlist[5], SQLlist[6], SQLlist[7], SQLlist[8], SQLlist[9], SQLlist[10], SQLlist[11], SQLlist[12]
                await __db.execute("INSERT INTO records (FIO, address, telephone, reason, information, for_master, master, record_value, Category, FIO_employee, RegDate, RecDate) \
                VALUES (:FIO, :address, :telephone, :reason, :information, :for_master, :master, :record_value, :Category, :FIO_employee, :RegDate, :RecDate)",
                    {
                        'FIO': __fio,
                        'address': __address,
                        'telephone': __telephone,
                        'reason': __reason,
                        'information': __information,
                        'for_master': __for_master,
                        'master': __master,
                        'record_value': __record_value,
                        'Category': __category,
                        'FIO_employee': __fio_employee,
                        'RegDate': __regdate,
                        'RecDate': __recdate
                    })
                await __db.commit()                         
                __msg = "Новая запись добавлена"
                return __msg
            except (DatabaseError, IndexError):
                self.log.error("Exception occurred", exc_info=True)
                raise
            finally:
                self.log.info(f"Новая заявка добавлена в БД")
    
    async def __delete(self, SQLlist=tuple()):
        async with connect("address_book.db") as __db:
            try:
                __address = SQLlist[1]
                __cursor = await __db.execute("DELETE FROM records\
                WHERE address = :address AND record_value = 'Закрыта'", {'address': __address})
                __msg = await __cursor.fetchall()
                await __db.commit()               
                if __msg:       
                    __msg = 'Запись удалена'            
                    return __msg
            except (DatabaseError, IndexError):
                self.log.error("Exception occurred", exc_info=True)
                raise
            finally:
                self.log.info(f"Запрос на удаление заявки выполнен")

    async def __update(self, SQLlist=tuple()):
        async with connect("address_book.db") as __db:
            try: 
                __fio, __address, __telephone, __reason, __information, __for_master,\
                __master, __record_value, __category, __recdate = SQLlist[1], SQLlist[2], SQLlist[3],\
                SQLlist[4], SQLlist[5], SQLlist[6], SQLlist[7], SQLlist[8], SQLlist[9], SQLlist[10]
                await __db.execute("UPDATE records \
                SET FIO = :FIO, address = :address, telephone = :telephone, reason = :reason, information = :information, for_master = :for_master, master = :master,\
                record_value = :record_value, Category = :Category, RecDate = :RecDate\
                WHERE address = :address",
                    {  
                        'FIO': __fio, 
                        'address': __address, 
                        'telephone': __telephone, 
                        'reason': __reason, 
                        'information': __information,
                        'for_master': __for_master, 
                        'master': __master, 
                        'record_value': __record_value,
                        'Category': __category,
                        'RecDate': __recdate
                    })
                await __db.commit()       
                __msg = "Запись обновлена"
                return __msg
            except (DatabaseError, IndexError):          
                self.log.error("Exception occurred", exc_info=True)
                raise
            finally:
                self.log.info(f"Запрос на обновление заявки выполнен")

    # Корутина, осуществляющая доступ к БД
    async def __access_db(self, SQLlist=tuple()):
        try:
            __db = await connect("address_book.db")
            __keyword = SQLlist[0]
        except (DatabaseError, IndexError):
            self.log.error("Exception occurred", exc_info=True)
            raise
        finally:
            if __keyword == "ENTER":
                __enter = await self.__enter(SQLlist)
                return __enter
            elif __keyword == "REGISTER":
                __register = await self.__register(SQLlist)
                return __register
            elif __keyword == "DELETEUSER":
                __deleteuser = await self.__deleteuser(SQLlist)
                return __deleteuser
            elif __keyword == "ALLQUERY":
                __allquery = await self.__allquery()
                return __allquery
            elif __keyword == "USERQUERY":
                __userquery = await self.__userquery()
                return __userquery
            elif __keyword == "CURQUERY":
                __curquery = await self.__curquery(SQLlist)
                return __curquery
            elif __keyword == "INSERT":
                __insert = await self.__insert(SQLlist)
                return __insert
            elif __keyword == "DELETE":
               __delete = await self.__delete(SQLlist)
               return __delete
            elif __keyword == "UPDATE":
                __update = await self.__update(SQLlist)
                return __update
            else:
                self.log.info(f"Поступил неправильный запрос")
                __MSG = "Неправильный запрос"
                return __MSG

    async def __accept_client(self, client_reader, client_writer):

        async def __client_done(task):
            del self.clients[task]
            client_writer.close()
            await client_writer.wait_closed()
            print('client task done', file = sys.stderr)
            self.log.info("Client task done")

        # start a new Task to handle this specific client connection
        try:
            task = asyncio.create_task(self.__handle_client(client_reader, client_writer))
        except (RuntimeError, asyncio.TimeoutError, asyncio.CancelledError, Exception):
            self.log.error("Exception occurred", exc_info=True)
            raise
        else:
            self.clients[task] = (client_reader, client_writer)
            done, pending = await asyncio.wait({task})
            if task in done:
                await __client_done(task)

    async def __handle_client(self, client_reader, client_writer):
        while True:
            try:
                line = (await client_reader.readline())
                if not line:
                    break
                line = await AsyncioBlockingIO().decrypt_message(line)
                line = line.split("^")
                if line:
                    try:
                        answer = await self.__access_db(SQLlist = line)
                        await self.__write_response(client_writer, answer)
                    except (RuntimeError, asyncio.TimeoutError, asyncio.CancelledError):
                        self.log.error("Exception occurred", exc_info=True)
                        raise
            except (asyncio.LimitOverrunError, asyncio.IncompleteReadError) as err:
                self.log.error("Exception occurred", exc_info=True)
                raise
            finally:
                await asyncio.sleep(1)

    async def __write_response(self, writer, IncData):
        try:
            addr = writer.get_extra_info('peername')
        except ConnectionResetError:
            self.log.error("Exception occurred", exc_info=True)
            raise
        finally:
            self.log.info(f"Connection accepted from {addr!r}")
            print(f"Received query from {addr!r}")
            try:
                __query = (await AsyncioBlockingIO().encrypt_message(IncData))
                __query_length = len(__query)
                __send_length = str(__query_length).encode('utf8')
                __send_length += b' ' * (self.__HEADER - len(__send_length))
            except TypeError:
                self.log.error("Exception occurred", exc_info=True)
                raise
            finally:
                try:
                    writer.write(__send_length)
                    writer.write(__query)
                except ConnectionResetError:
                    self.log.error("Exception occurred", exc_info=True)
                    raise
                finally:
                    await writer.drain()

    async def start(self):

        self.__server = await asyncio.start_server(self.__accept_client, host = 'localhost', port = 43333, \
        family = socket.AF_INET, backlog = 20, reuse_address = True)

        addr = self.__server.sockets[0].getsockname()
        log.info(f'Serving on {addr}')
        print(f'Serving on {addr}')

        async with self.__server:
            await self.__server.serve_forever()

if __name__ == "__main__":
    Server = MyServer()
    aiolog.start()
    log = logging.getLogger('')
    f_format = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log.setLevel(logging.INFO)
    f_handler = logging.FileHandler('ServerLog.log')
    f_handler.setLevel(logging.INFO)
    f_handler.setFormatter(f_format)
    log.addHandler(f_handler) 
    asyncio.run(Server.start(), debug = True)
    loop = asyncio.get_running_loop()
    if loop.get_debug():
        log.debug("Some exception")