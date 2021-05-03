import asyncio
import sys
import socket
import logging
import random
try:
    import aiolog
    from aiosqlite import connect, DatabaseError
    from AIOEncryption import AsyncioBlockingIO
except ImportError:
    raise

class MyServer:
    """My example of asyncio TCP server,
       with some db functionality,
       using Python 3.9.1
       writen in EAFP code style
    """
    HEADER = 64

    def __init__(self):
        """constracts or class as object"""
        self.log = logging.getLogger(__name__)

        self.clients = {}

    async def enter(self, db, SQLlist=tuple()):
        try:
            Log, Passs = SQLlist[1], SQLlist[2]
            cursor = await db.execute("SELECT IIF(Login = :Login,\
                                      (SELECT Password FROM Cipher), 'NOLOG'), IIF(Login = :Login,\
                                      (SELECT employee_FIO FROM Cipher), 'NOLOG') FROM Cipher",
                                      {'Login': Log})
            msg = await cursor.fetchall()

            for i in msg:
                if i[0] == "NOLOG":
                    self.log.info("Попытка входа с неправильным логином")
                    return i[0]
                else:
                    check_ = (await asyncio.wait_for(\
                                                     AsyncioBlockingIO().check_pass(Passs, i[0]), timeout=5.0))
                    if check_:
                        self.log.info(f"Сотрудник {Log} авторизировался")
                        msg = "^".join(["GO", i[1]])
                    else:
                        self.log.info("Попытка входа с неправильным логином")
                        msg = "Fail"

        except (OSError, DatabaseError, IndexError, Exception):
            self.log.error("Exception occurred", exc_info=True)
            raise
        finally:
            return msg

    async def register(self, db, SQLlist=tuple()):
        """Register new User in our database with hashed password"""

        try:
            id_, login, password, fio = SQLlist[1], SQLlist[2], SQLlist[3], SQLlist[4]

            new_hash = (await asyncio.wait_for(\
                                               AsyncioBlockingIO().to_hash_password(password), timeout=5.0))
            cursor = await db.execute("INSERT INTO Cipher (ID, Login, Password, employee_FIO)\
                                       VALUES (:ID, :Login, :Password, :employee_FIO)",\
                                       {'ID': id_, 'Login': login, 'Password': new_hash, 'employee_FIO': fio})
            await db.commit()

            self.log.info(f"Сотрудник {fio} зарегистрирован")
        except (OSError, DatabaseError, IndexError, Exception):
            self.log.error("Exception occurred", exc_info=True)
            raise
        finally:
            msg = 'Reg'
            return msg

    async def deleteuser(self, db, SQLlist=tuple()):
        try:
            id_ = SQLlist[1]
            await db.execute("DELETE FROM Cipher WHERE ID = :ID", {'ID': id_})
            await db.commit()
        except (OSError, DatabaseError, IndexError, Exception):
            self.log.error("Exception occurred", exc_info=True)
            raise
        finally:
            self.log.info(f"Сотрудник {id_} удален из БД")
            msg = "OK"
            return msg

    async def allquery(self, db):
        try:
            cursor = await db.execute("SELECT RecDate, FIO, address,\
                                       telephone, reason, information, for_master, master, record_value,\
                                       Category, FIO_employee, RegDate FROM records")
            records = await cursor.fetchall()

            print_records = ''
            for record in records:
                print_records += '^'.join((str(record[0]), str(record[1]),\
                                           str(record[2]), str(record[3]), str(record[4]),\
                                           str(record[5]), str(record[6]), str(record[7]),\
                                           str(record[8]), str(record[9]), str(record[10]), str(record[11]),'#'))

        except (OSError, DatabaseError, IndexError, Exception):
            self.log.error("Exception occurred", exc_info=True)
            raise
        finally:
            self.log.info("Запрос на все заявки")
            return print_records

    async def userquery(self, db):
        try:
            cursor = await db.execute("SELECT ID, Login, Password,\
                                       employee_FIO FROM Cipher")
            records = await cursor.fetchall()

            print_logins = ''
            for record in records:
                print_logins += '^'.join((str(record[0]), str(record[1]),\
                                          str(record[2]), str(record[3]), '#'))

        except (OSError, DatabaseError, IndexError, Exception):
            self.log.error("Exception occurred", exc_info=True)
            raise
        finally:
            self.log.info("Запрос на информацию о сотрудниках")
            return print_logins

    async def curquery(self, db, SQLlist=tuple()):
        try:
            recdate = SQLlist[1]
            print_records = ''
            cursor = await db.execute("SELECT RecDate, FIO, address, telephone,\
                                       reason, information, for_master, master, record_value, Category,\
                                       FIO_employee, RegDate FROM records WHERE RecDate = :RecDate",\
                                       {'RecDate': recdate})
            records = await cursor.fetchall()

            if records == []:
                print("На текущий день ничего нет")
                print_records = 'No'
            else:
                self.log.info("Запрос на текущие заявки")
                for record in records:
                    print_records += '^'.join((str(record[0]), str(record[1]),\
                                               str(record[2]), str(record[3]), str(record[4]), str(record[5]),\
                                               str(record[6]), str(record[7]), str(record[8]), str(record[9]),\
                                               str(record[10]), str(record[11]),'#'))

        except (OSError, DatabaseError, IndexError, Exception):
            self.log.error("Exception occurred", exc_info=True)
            raise
        finally:
            return print_records

    async def insert(self, db, SQLlist=tuple()):
        try:
            fio, address, telephone, reason, information, for_master,\
            master, record_value, category, fio_employee, regdate, recdate =\
                                                                            SQLlist[1], SQLlist[2], SQLlist[3],\
                                                                            SQLlist[4], SQLlist[5], SQLlist[6], SQLlist[7],\
                                                                            SQLlist[8], SQLlist[9], SQLlist[10], SQLlist[11], SQLlist[12]

            await db.execute("INSERT INTO records (FIO, address, telephone, reason,\
                              information, for_master, master, record_value, Category,\
                              FIO_employee, RegDate, RecDate)\
                              VALUES (:FIO, :address, :telephone, :reason, :information,\
                              :for_master, :master, :record_value, :Category, :FIO_employee,\
                              :RegDate, :RecDate)",
                              {
                                'FIO': fio,
                                'address': address,
                                'telephone': telephone,
                                'reason': reason,
                                'information': information,
                                'for_master': for_master,
                                'master': master,
                                'record_value': record_value,
                                'Category': category,
                                'FIO_employee': fio_employee,
                                'RegDate': regdate,
                                'RecDate': recdate
                              })
            await db.commit()
        except (OSError, DatabaseError, IndexError, Exception):
            self.log.error("Exception occurred", exc_info=True)
            raise
        finally:
            self.log.info(f"Новая заявка добавлена в БД")
            msg = "Новая запись добавлена"
            return msg

    async def delete(self, db, SQLlist=tuple()):
        try:
            address = SQLlist[1]
            cursor = await db.execute("DELETE FROM records\
                                       WHERE address = :address AND\
                                       record_value = 'Закрыта'", {'address': address})
            await db.commit()
        except (OSError, DatabaseError, IndexError, Exception):
            self.log.error("Exception occurred", exc_info=True)
            raise
        finally:
            self.log.info("Запрос на удаление заявки выполнен")
            msg = 'Запись удалена'
            return msg

    async def update(self, db, SQLlist=tuple()):
        try:
            fio, address, telephone, reason, information, for_master,\
            master, record_value, category, recdate =\
                                                      SQLlist[1], SQLlist[2], SQLlist[3],\
                                                      SQLlist[4], SQLlist[5], SQLlist[6],\
                                                      SQLlist[7], SQLlist[8], SQLlist[9], SQLlist[10]

            await db.execute("UPDATE records\
                              SET FIO = :FIO, address = :address, telephone = :telephone,\
                              reason = :reason, information = :information,\
                              for_master = :for_master, master = :master,\
                              record_value = :record_value, Category = :Category, RecDate = :RecDate\
                              WHERE address = :address",
                              {
                                'FIO': fio,
                                'address': address,
                                'telephone': telephone,
                                'reason': reason,
                                'information': information,
                                'for_master': for_master,
                                'master': master,
                                'record_value': record_value,
                                'Category': category,
                                'RecDate': recdate
                              })
            await db.commit()
        except (OSError, DatabaseError, IndexError, Exception):
            self.log.error("Exception occurred", exc_info=True)
            raise
        finally:
            self.log.info("Запрос на обновление заявки выполнен")
            msg = "Запись обновлена"
            return msg

    async def access_db(self, SQLlist=tuple()):
        """This funcions is used to connect
           database and get required data
           required data is defines
           via keyword from client
        """

        try:
            keyword = SQLlist[0]
        except IndexError:
            self.log.error("Exception occurred", exc_info=True)
            raise
        finally:
            try:
                async with connect("address_book.db") as db:
                    if keyword == "ENTER":
                        data = (await asyncio.shield(\
                                      asyncio.wait_for(\
                                                       self.enter(db, SQLlist), timeout=5.0)))
                    elif keyword == "REGISTER":
                        data = (await asyncio.shield(\
                                      asyncio.wait_for(\
                                                      self.register(db, SQLlist), timeout=5.0)))
                    elif keyword == "DELETEUSER":
                        data = (await asyncio.shield(\
                                      asyncio.wait_for(\
                                                       self.deleteuser(db, SQLlist), timeout=5.0)))
                    elif keyword == "ALLQUERY":
                        data = (await asyncio.shield(\
                                      asyncio.wait_for(\
                                                       self.allquery(db), timeout=5.0)))
                    elif keyword == "USERQUERY":
                        data = (await asyncio.shield(\
                                      asyncio.wait_for(\
                                                       self.userquery(db), timeout=5.0)))
                    elif keyword == "CURQUERY":
                        data = (await asyncio.shield(\
                                      asyncio.wait_for(\
                                                       self.curquery(db, SQLlist), timeout=5.0)))
                    elif keyword == "INSERT":
                        data = (await asyncio.shield(\
                                      asyncio.wait_for(\
                                                       self.insert(db, SQLlist), timeout=5.0)))
                    elif keyword == "DELETE":
                        data = (await asyncio.shield(\
                                      asyncio.wait_for(\
                                                       self.delete(db, SQLlist), timeout=5.0)))
                    elif keyword == "UPDATE":
                        data = (await asyncio.shield(\
                                      asyncio.wait_for(\
                                                       self.update(db, SQLlist), timeout=5.0)))
                    else:
                        self.log.info("Поступил неправильный запрос")
                        data = "Неправильный запрос"
            except (Exception, OSError, DatabaseError, RuntimeError):
                self.log.error("Exception occured", exc_info=True)
                raise
            finally:
                return data

    async def accept_client(self, client_reader, client_writer):
        """This function is used to accept client connection"""

        # when hadle_client Task in done state, closing connection
        # and deleting connection from connections list
        async def client_done(task):
            del self.clients[task]
            print("client task done", file = sys.stderr)
            client_writer.close()
            await client_writer.wait_closed()

        # start a new Task to handle this specific client connection
        try:
            handle_task = asyncio.create_task(\
                                              self.handle_client(client_reader, client_writer))
        except (OSError, RuntimeError, asyncio.TimeoutError, asyncio.CancelledError):
            self.log.error("Exception occurred", exc_info=True)
            raise
        finally:
            try:
                self.clients[handle_task] = (client_reader, client_writer)
                done, pending = await asyncio.shield(\
                                      asyncio.wait({handle_task}))
            except (OSError, RuntimeError, asyncio.TimeoutError, asyncio.CancelledError):
                self.log.error("Exception occurred", exc_info=True)
                raise
            finally:
                if handle_task in done:
                    handle_task.cancel()
                    done_task = asyncio.create_task(client_done(handle_task))
                    done, pending = await asyncio.shield(\
                                          asyncio.wait({done_task}))
                    if done_task in done:
                        done_task.cancel()

    async def handle_client(self, client_reader, client_writer):
        """handles incoming TCP connection from client"""

        # blocking loop on random time to avoid deadlock
        await asyncio.sleep(1 ** (1 / random.random()))
        while True:
            # client_reader waits to reads data till EOF '\n'
            read_data_task = asyncio.create_task(client_reader.readline())
            # if connection established
            if read_data_task:
                done, pending = await asyncio.shield(\
                                      asyncio.wait({read_data_task}))
                if read_data_task in done:
                    received_query = read_data_task.result()
                    decrypt_data_task = asyncio.create_task(\
                                                            AsyncioBlockingIO().decrypt_message(received_query))
                    done, pending = await asyncio.shield(\
                                          asyncio.wait({decrypt_data_task}))
                    if decrypt_data_task in done:
                        decrypted_data = decrypt_data_task.result()
                        message = decrypted_data.split("^")
                        try:
                            addr = client_writer.get_extra_info('peername')
                            self.log.info(f"Connected to {addr}")
                            print(f"Connected to {addr}")

                            db_task = asyncio.create_task(self.access_db(SQLlist=message))
                            done, pending = await asyncio.shield(\
                                                  asyncio.wait({db_task}))
                            if db_task in done:
                                data_from_db = db_task.result()
                                self.log.info("query in database done great")
                                print("query in database done great")
                                write_task = asyncio.create_task(\
                                                                 self.write_response(client_writer, data_from_db))
                                done, pending = await asyncio.shield(\
                                                      asyncio.wait({write_task}))
                                if write_task in done:
                                    self.log.info("writer writed response to client, yeahhhh")
                                    print("writer writed response to client, yeahhhh")
                                    tasks = [read_data_task, decrypt_data_task, db_task, write_task]
                                    cancel_ = [task.cancel() for task in tasks]
                                    if cancel_:
                                        print('tasks canceled succesfully')
                                        return
                        except (OSError, RuntimeError, Exception,\
                                asyncio.TimeoutError, asyncio.CancelledError, asyncio.InvalidStateError):
                            self.log.error("Exception occurred", exc_info=True)
                            raise

    async def write_response(self, client_writer, data):
        """This function encrypting data from DB query
           and sends it to our client
        """

        # Encrypts a new message and calculate it's length to send
        encrypt_task = asyncio.create_task(AsyncioBlockingIO().encrypt_message(data))
        done, pending = await asyncio.shield(\
                              asyncio.wait({encrypt_task}))
        if encrypt_task in done:
            query = encrypt_task.result()
            query_length = len(query)
            send_length = str(query_length).encode('utf8')
            send_length += b' ' * (self.HEADER - len(send_length))
            try:
                client_writer.write(send_length)
                client_writer.write(query)
            except (Exception, OSError, ConnectionError, RuntimeError,\
                    asyncio.CancelledError, asyncio.InvalidStateError, asyncio.TimeoutError):
                self.log.error("Exception occured", exc_info=True)
                raise
            finally:
                await client_writer.drain()
                encrypt_task.cancel()

    async def start(self):
        """This function starts our async TCP server
           in event loop, reader and writer is passed to
           coroutine accept_client, that responsible for
           creating 'client connections' tasks in our server
           that handles incoming connections
        """
        self.server = await asyncio.start_server(self.accept_client,\
                                                 host='localhost', port=43333,\
                                                 family=socket.AF_INET,\
                                                 backlog=20, reuse_address=True)

        addr = self.server.sockets[0].getsockname()
        log.info(f'Serving on {addr}')
        print(f'Serving on {addr}')

        async with self.server:
            await self.server.serve_forever()

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
    try:
        # Starting our server and loop with debug mode
        asyncio.run(Server.start(), debug=True)
        loop = asyncio.get_running_loop()
        if loop.get_debug():
            log.debug("Some exception")
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()