import asyncio
import sys
from socket import AF_INET
import logging
from weakref import WeakKeyDictionary
from itertools import chain, product
import time
try:
    from aiosqlite import connect, DatabaseError, ProgrammingError,\
                          OperationalError, NotSupportedError
    from AIOEncryption import AsyncioBlockingIO
except ImportError as exc:
    print(exc)
    time.sleep(20)

class MyServer:
    """My example of asyncio TCP server,
       with some db functionality,
       using Python 3.9.1
       writen in EAFP and code style

       Мой пример Асинхронного TCP сервера
       с запросами в БД, используется python 3.9.1
       в EAFP стиле
    """

    def __init__(self):

        # this keep tracking all client tasks inside
        self.clients = WeakKeyDictionary()

    async def iterate_(self, data):
        try:
            s = chain(*product(data, '#'))
            s = map(str, chain.from_iterable(s))
            s = '^'.join((*s,))
        except AttributeError:
            log.error("Exception occurred", exc_info=True)
            raise
        else:
            return s

    async def enter(self, db, SQLlist):
        try:
            cursor = await db.execute("SELECT Password \
                                       FROM Cipher \
                                       WHERE Login = :Login",
                                     {'Login': SQLlist[1]})
            cursor = await cursor.fetchone()
            if cursor:
                check_ = (await asyncio.wait_for(\
                                                 AsyncioBlockingIO().check_pass(SQLlist[2], cursor[0]), timeout=2.0))
                if check_:
                    cursor = await db.execute("SELECT employee_FIO \
                                               FROM Cipher \
                                               WHERE Login = :Login",
                                              {'Login': SQLlist[1]})
                    cursor = await cursor.fetchone()
                    log.info(f"Сотрудник {SQLlist[1]} авторизировался")
                    cursor = "^".join(["GO", cursor[0]])
                else:
                    log.info("Попытка входа с неправильным паролем")
                    cursor = "Fail"
            else:
                cursor = "NOLOG"
        except (AttributeError, IndexError,\
                OperationalError, ProgrammingError):
            log.error("Exception occurred", exc_info=True)
            raise
        else:
            return cursor

    async def register(self, db, SQLlist):
        try:
            new_hash = (await asyncio.wait_for(\
                                               AsyncioBlockingIO().to_hash_password(SQLlist[3]), timeout=2.0))
            await db.execute("INSERT INTO Cipher (ID, Login, Password, employee_FIO)\
                              VALUES (:ID, :Login, :Password, :employee_FIO)",
                            {'ID': SQLlist[1], 'Login': SQLlist[2],
                             'Password': new_hash, 'employee_FIO': SQLlist[4]})
            await db.commit()

            log.info(f"Сотрудник {SQLlist[4]} зарегистрирован")
        except (AttributeError, IndexError,\
                OperationalError, ProgrammingError):
            log.error("Exception occurred", exc_info=True)
            raise
        else:
            msg = 'Reg'
            return msg

    async def changeuser(self, db, SQLlist):
        try:
            new_hash = (await asyncio.wait_for(\
                                               AsyncioBlockingIO().to_hash_password(SQLlist[3]), timeout=2.0))
            await db.execute("UPDATE Cipher \
                              SET Login = :Login, Password = :Password,\
                                  employee_FIO = :employee_FIO \
                              WHERE ID = :ID",
                            {'ID': SQLlist[1], 'Login': SQLlist[2],
                             'Password': new_hash, 'employee_FIO': SQLlist[4]})
            await db.commit()
        except (AttributeError, IndexError,\
                OperationalError, ProgrammingError):
            log.error("Exception occured", exc_info=True)
            raise
        else:
            log.info(f"Сотрудник {SQLlist[2]} изменён")
            msg = "OK"
            return msg

    async def deleteuser(self, db, SQLlist):
        try:
            await db.execute("DELETE FROM Cipher\
                              WHERE ID = :ID",
                            {'ID': SQLlist[1]})
            await db.commit()
        except (AttributeError, IndexError,\
                OperationalError, ProgrammingError):
            log.error("Exception occurred", exc_info=True)
            raise
        else:
            log.info(f"Сотрудник {SQLlist[1]} удален из БД")
            msg = "OK"
            return msg

    async def allquery(self, db):
        try:
            cursor = await db.execute("SELECT rec_date, FIO, address,\
                                              telephone, reason, current_tariff, realization_time,\
                                              for_master, master, record_state,\
                                              category, employee_FIO, reg_date, ID\
                                       FROM records")
            cursor = await cursor.fetchall()

            cursor = await self.iterate_(cursor)

        except (AttributeError, DatabaseError,\
                OperationalError, ProgrammingError):
            log.error("Exception occurred", exc_info=True)
            raise
        else:
            log.info("Запрос на все заявки")
            return cursor

    async def userquery(self, db):
        try:
            cursor = await db.execute("SELECT ID, Login,\
                                              Password, employee_FIO \
                                       FROM Cipher")
            cursor = await cursor.fetchall()
            cursor = await self.iterate_(cursor)

        except (AttributeError, DatabaseError,\
                OperationalError, ProgrammingError):
            log.error("Exception occurred", exc_info=True)
            raise
        else:
            log.info("Запрос на информацию о сотрудниках")
            return cursor

    async def curquery(self, db, SQLlist):
        try:
            cursor = await db.execute("SELECT rec_date, FIO, address, telephone,\
                                              reason, current_tariff, realization_time,\
                                              for_master, master, record_state, category,\
                                              employee_FIO, reg_date, ID\
                                       FROM records \
                                       WHERE rec_date = :rec_date",
                                     {'rec_date': SQLlist[1]})
            cursor = await cursor.fetchall()

            if cursor == []:
                print("На текущий день ничего нет")
                cursor = 'No'
            else:
                log.info("Запрос на текущие заявки")
                cursor = await self.iterate_(cursor)

        except (AttributeError, IndexError,\
                OperationalError, ProgrammingError):
            log.error("Exception occurred", exc_info=True)
            raise
        else:
            return cursor

    async def insert(self, db, SQLlist):
        try:
            await db.execute("INSERT INTO records (category, FIO, address, telephone,\
                                                   reason, current_tariff, realization_time, for_master, master,\
                                                   rec_date, record_state, reg_date, employee_FIO)\
                              VALUES (:category, :FIO, :address, :telephone, :reason,\
                                      :current_tariff, :realization_time, :for_master, :master, :rec_date,\
                                      :record_state, :reg_date, :employee_FIO)",\
                            {
                              'category': SQLlist[1],
                              'FIO': SQLlist[2],
                              'address': SQLlist[3],
                              'telephone': SQLlist[4],
                              'reason': SQLlist[5],
                              'current_tariff': SQLlist[6],
                              'realization_time': SQLlist[7],
                              'for_master': SQLlist[8],
                              'master': SQLlist[9],
                              'rec_date': SQLlist[10],
                              'record_state': SQLlist[11],
                              'reg_date': SQLlist[12],
                              'employee_FIO': SQLlist[13]
                            })
            await db.commit()
        except (AttributeError, IndexError,\
                OperationalError, ProgrammingError):
            log.error("Exception occurred", exc_info=True)
            raise
        else:
            log.info(f"Новая заявка добавлена в БД")
            msg = "Новая запись добавлена"
            return msg

    async def delete(self, db, SQLlist):
        try:
            await db.execute("DELETE FROM records\
                              WHERE ID = :ID",
                            {'ID': SQLlist[1]})
            await db.commit()
        except (AttributeError, IndexError,\
                OperationalError, ProgrammingError):
            log.error("Exception occurred", exc_info=True)
            raise
        else:
            log.info("Запрос на удаление заявки выполнен")
            msg = 'Запись удалена'
            return msg

    async def update(self, db, SQLlist):
        try:
            await db.execute("UPDATE records\
                              SET category = :category, FIO = :FIO, address = :address,\
                                  telephone = :telephone, reason = :reason, realization_time = :realization_time,\
                                  for_master = :for_master, master = :master, record_state = :record_state,\
                                  rec_date = :rec_date, current_tariff = :current_tariff\
                              WHERE ID = :ID",
                            {
                              'ID': SQLlist[1],
                              'category': SQLlist[2],
                              'FIO': SQLlist[3],
                              'address': SQLlist[4],
                              'telephone': SQLlist[5],
                              'reason': SQLlist[6],
                              'realization_time': SQLlist[7],
                              'for_master': SQLlist[8],
                              'master': SQLlist[9],
                              'record_state': SQLlist[10],
                              'rec_date': SQLlist[11],
                              'current_tariff': SQLlist[12]
                            })
            await db.commit()
        except (AttributeError, IndexError,\
                OperationalError, ProgrammingError):
            log.error("Exception occurred", exc_info=True)
            raise
        else:
            log.info("Запрос на обновление заявки выполнен")
            msg = "Запись обновлена"
            return msg

    async def access_db(self, SQLlist=list()):
        """This coroutine is used for DB connection
           required data is defines via keyword from client

           Эта корутина предназначена для соединения с БД
           запрашиваемые данные определяются с помощью
           ключевого слова, которое посылает клиент
        """

        try:
            keyword = SQLlist[0]
        except IndexError:
            log.error("Exception occurred", exc_info=True)
            raise
        else:
            try:
                async with connect("address_book.db") as db:
                    if keyword == "ENTER":
                        enter_ = await asyncio.shield(\
                                       asyncio.wait_for(\
                                                        self.enter(db, SQLlist), timeout=2.0))
                        return enter_
                    elif keyword == "REGISTER":
                        register_ = await asyncio.shield(\
                                          asyncio.wait_for(\
                                                           self.register(db, SQLlist), timeout=2.0))
                        return register_
                    elif keyword == "DELETEUSER":
                        delete_user_ = await asyncio.shield(\
                                             asyncio.wait_for(\
                                                              self.deleteuser(db, SQLlist), timeout=2.0))
                        return delete_user_
                    elif keyword == "ALLQUERY":
                        all_query_ = await asyncio.shield(\
                                           asyncio.wait_for(\
                                                            self.allquery(db), timeout=2.0))
                        return all_query_
                    elif keyword == "USERQUERY":
                        user_query_ = await asyncio.shield(\
                                            asyncio.wait_for(\
                                                             self.userquery(db), timeout=2.0))
                        return user_query_
                    elif keyword == "CURQUERY":
                        cur_query_ = await asyncio.shield(\
                                           asyncio.wait_for(\
                                                            self.curquery(db, SQLlist), timeout=2.0))
                        return cur_query_
                    elif keyword == "INSERT":
                        insert_ = await asyncio.shield(\
                                        asyncio.wait_for(\
                                                         self.insert(db, SQLlist), timeout=2.0))
                        return insert_
                    elif keyword == "DELETE":
                        delete_ = await asyncio.shield(\
                                        asyncio.wait_for(\
                                                         self.delete(db, SQLlist), timeout=2.0))
                        return delete_
                    elif keyword == "UPDATE":
                        update_ = await asyncio.shield(\
                                        asyncio.wait_for(\
                                                         self.update(db, SQLlist), timeout=2.0))
                        return update_
                    elif keyword == "CHANGEUSER":
                        update_user = await asyncio.shield(\
                                            asyncio.wait_for(\
                                                             self.changeuser(db, SQLlist), timeout=2.0))
                        return update_user
                    else:
                        log.info("Поступил неправильный запрос")
                        wrong_query = "Неправильный запрос"
                        return wrong_query
            except (NotSupportedError, DatabaseError,\
                    asyncio.TimeoutError, asyncio.CancelledError):
                log.error("Exception occured", exc_info=True)
                raise

    # when hadle_client Task in done state, closing connection
    # and deleting connection from connections list
    async def client_done(self, task, client_writer):
        try:
            del self.clients[task]
            print("client task done", file = sys.stderr)
            client_writer.close()
            await client_writer.wait_closed()
        except (IOError, Exception):
            log.error("Exception occurred", exc_info=True)
            raise
        else:
            return

    async def accept_client(self, client_reader, client_writer):
        """This coroutine is used to accept client connection

           Эта корутина используется для обработки соединений
           от TCP клиента
        """

        # start a new Task to handle this specific client connection
        try:
            handle_task = asyncio.create_task(\
                                              self.handle_client(client_reader, client_writer))
        except (asyncio.TimeoutError, asyncio.CancelledError,\
                asyncio.IncompleteReadError, asyncio.InvalidStateError):
            log.error("Exception occurred", exc_info=True)
            raise
        else:
            try:
                self.clients[handle_task] = client_reader, client_writer
                done, pending = await asyncio.shield(\
                                      asyncio.wait({handle_task}))
            except (asyncio.TimeoutError, asyncio.CancelledError):
                log.error("Exception occurred", exc_info=True)
                handle_task.cancel()
                raise
            else:
                if handle_task in done:
                    handle_task.cancel()
                    try:
                        done_task = asyncio.create_task(\
                                                        self.client_done(handle_task, client_writer))
                        done, pending = await asyncio.shield(\
                                              asyncio.wait({done_task}))
                    except (asyncio.TimeoutError, asyncio.CancelledError,
                            asyncio.InvalidStateError):
                        log.error("Exception occurred", exc_info=True)
                        done_task.cancel()
                        raise
                    else:
                        if done_task in done:
                            done_task.cancel()

    async def handle_client(self, client_reader, client_writer):
        """handles incoming TCP connection from client

           обрабатывает запрос клиента
        """

        while True:
            # client_reader waits to reads data till EOF '\n'
            try:
                read_data_task = asyncio.create_task(client_reader.readline())
            except (asyncio.TimeoutError, asyncio.IncompleteReadError,\
                    asyncio.InvalidStateError):
                log.error("Exception occured", exc_info=True)
                raise
            else:
                # if connection established
                if read_data_task:
                    done, pending = await asyncio.shield(\
                                          asyncio.wait({read_data_task}))
                    if read_data_task in done:
                        try:
                            received_query = read_data_task.result()
                            # this Task decrypts client message
                            decrypt_data_task = asyncio.create_task(\
                                                                    AsyncioBlockingIO().decrypt_message(received_query))
                            done, pending = await asyncio.shield(\
                                                  asyncio.wait({decrypt_data_task}))
                        except (asyncio.InvalidStateError, asyncio.TimeoutError,\
                                asyncio.CancelledError):
                            log.error("Exception occurred", exc_info=True)
                            decrypt_data_task.cancel()
                            raise
                        else:
                            if decrypt_data_task in done:
                                try:
                                    decrypted_data = decrypt_data_task.result()
                                    message = decrypted_data.split("^")
                                    addr = client_writer.get_extra_info('peername')
                                    print(f"Connected to {addr!r}")
                                    log.info(f"Connected to {addr!r}")

                                    db_task = asyncio.create_task(self.access_db(SQLlist=message))
                                    done, pending = await asyncio.shield(\
                                                          asyncio.wait({db_task}))
                                except (asyncio.TimeoutError, asyncio.CancelledError,\
                                        asyncio.InvalidStateError):
                                    log.error("Exception occurred", exc_info=True)
                                    db_task.cancel()
                                    raise
                                else:
                                    if db_task in done:
                                        try:
                                            data_from_db = db_task.result()
                                            # wait untill writer is ready
                                            write_task = asyncio.create_task(\
                                                                             self.write_response(client_writer, data_from_db))
                                            done, pending = await asyncio.shield(\
                                                                  asyncio.wait({write_task}))
                                        except (asyncio.TimeoutError, asyncio.CancelledError,\
                                                asyncio.InvalidStateError):
                                            log.error("Exception occurred", exc_info=True)
                                            write_task.cancel()
                                            raise
                                        finally:
                                            # when write Task is done, .cancel all Tasks
                                            if write_task in done:
                                                try:
                                                    print("Connection finished")
                                                    return
                                                except (asyncio.TimeoutError, asyncio.CancelledError,\
                                                        asyncio.InvalidStateError):
                                                    log.error("Exception occurred", exc_info=True)
                                                    raise
                else:
                    break

    async def write_response(self, client_writer, data):
        """This function encrypting data from DB query
           and sends it to our client

           Эта функция зашифровывает данные из БД
           и отправляет их клиенту
        """

        # Encrypts a new message and calculate it's length to send
        try:
            encrypt_task = asyncio.create_task(\
                                               AsyncioBlockingIO().encrypt_message(data))
            done, pending = await asyncio.shield(\
                                  asyncio.wait({encrypt_task}))
        except (asyncio.TimeoutError, asyncio.CancelledError,\
                asyncio.InvalidStateError):
            log.error("Exception occurred", exc_info=True)
            raise
        else:
            if encrypt_task in done:
                try:
                    query = encrypt_task.result()
                except Exception:
                    log.error("Exception occurred", exc_info=True)
                    raise
                else:
                    try:
                        client_writer.write(query)
                    except (asyncio.SendfileNotAvailableError, IOError):
                        log.error("Exception occured", exc_info=True)
                        raise
                    else:
                        await client_writer.drain()

    async def start(self):
        """This coroutine starts our async TCP server
           in event loop, reader and writer is passed to
           coroutine accept_client, that responsible for
           creating 'client connections' tasks in our server
           that handles incoming connections

           Эта корутина запускает наш асинхронный сервер
           в петле событий, reader и writer передаются
           корутине accept_client, которая ответственна
           за создание задания на соединение между сервером и клиентом
        """
        self.server = await asyncio.start_server(self.accept_client,\
                                                 host='172.20.20.14', port=43333,\
                                                 family=AF_INET,\
                                                 backlog=20, reuse_address=True)

        addr = self.server.sockets[0].getsockname()
        log.info(f'Serving on {addr!r}')
        print(f'Serving on {addr!r}')

        async with self.server:
            await self.server.serve_forever()

if __name__ == "__main__":
    try:
        Server = MyServer()
        log = logging.getLogger('asyncio')
        f_format = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        log.setLevel(logging.INFO)
        f_handler = logging.FileHandler('ServerLog.log')
        f_handler.setFormatter(f_format)
        log.addHandler(f_handler)
    except Exception as exc:
        print(exc)
        time.sleep(20)
    else:
        try:
            # Starting our server and loop with debug mode
            asyncio.run(Server.start(), debug=True)
            loop = asyncio.get_running_loop()
            if loop.get_debug():
                log.debug("Some exception")
        except KeyboardInterrupt:
            pass