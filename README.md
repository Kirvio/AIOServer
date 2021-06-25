# AIOServer
The purpose of this project is to better manage requests from clients to call the master

  as a server i'm using asyncio TCP server to handle connection from TCP client

  DB: aiosqlite
  
  How to use:
  
    make sure you use Python 3.9(python --version)
    
    install all needed modules that this programm uses like:
      pip3 install aiosqlite
      pip3 install cryptography
      pip3 install xlsxwriter
      pip3 install tkcalendar
      pip3 install bcrypt
    put all .py and .pyw scripts in the same folder
    create .db file with aiosqlite and some table with it(write your own queries)
    (create table some users etc, etc)
    to register some users put Registration class instead Authorization in (if __name__ == "__main__":)
    create key for encryption/decryption with Fernet(Fernet.generate_key()) and put it into file
    write path to your key file in path variables(__key_path)
    and write your own host='172.20.20.14', port=43333 in AsyncioServer and Encrypt module
  This is basically it, hf
  
  Instruction for russian users, is in Instruction folder
