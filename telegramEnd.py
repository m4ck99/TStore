from pyrogram import Client
from pyrogram.raw import functions, types
import os
from fileToBlobs import toChunks, fromChunks
import sqlite3 as sq
import hashlib

creds = open('cred.txt').readlines()
api_id = creds[0].strip('\n')
api_hash = creds[1].strip('\n')

app = Client("tstore", api_id=api_id, api_hash=api_hash)
connection = sq.connect('server/instance/test.db')
cursor = connection.cursor()


async def progress(current, total):
    print(f"{round((current / total) * 100)}%", end='\r')

async def upload(fullPath, filename, md5Hash, chatid):
    data = open(fullPath, 'rb').read()
    chunks = toChunks(data, fullPath)
    for index, part in enumerate(chunks):
        with open(f'chunked/{index}', 'wb') as f:
            f.write(part)
    for file in os.listdir('chunked'):
        await app.send_document(chatid, f'chunked/{file}', file_name=f'{md5Hash};{file}', caption=f'{md5Hash};{file}', progress=progress)

async def download(md5Hash, filename, chatid):
    fileList = []
    async for message in app.get_chat_history(chatid):
        if message.caption != None and (message.caption).split(';')[0] == md5Hash:
            fileList.append((message.document.file_id, (message.caption).split(';')[1]))
    for file in fileList:
        await app.download_media(file[0], file_name=file[1])
    fromChunks('downloads', filename)

async def main():
    async with app:
        if '.initiated' not in os.listdir():
            await app.create_group("TStore", "me")
            with open('./.initiated', 'w') as f:
                f.write('')
        async for dialog in app.get_dialogs():
            if dialog.chat.title == 'TStore':
                chatId = dialog.chat.id
                print(f'chat_id: {chatId}')
                while True:
                    cursor.execute('SELECT * FROM todo')  # Adjust table name as needed

                    # Fetch all rows
                    rows = cursor.fetchall()
                    
                    # Get column names
                    column_names = [description[0] for description in cursor.description]
                    file_location_index = column_names.index('location')
                    md5_index = column_names.index('md5hash')
                    action_index = column_names.index('action')
                    filename_index = column_names.index('fileName')
                    
                    for row in rows:
                        action = row[action_index]
                        filelocation = row[file_location_index]
                        md5 = row[md5_index]
                        filEname = row[filename_index]
                        if action == 'upload':
                            print("uploading")
                            await upload(filelocation, filEname, md5, chatId)
                            cursor.execute('UPDATE todo SET action = "" WHERE action = "upload"')
                            connection.commit()
                           
                        elif action == 'download':
                            print("Download Started")
                            await download(md5, filEname, chatId)
                            cursor.execute('UPDATE todo SET action = "" WHERE action = "download"')
                            connection.commit()
                            print('Downloaded')
app.run(main())

