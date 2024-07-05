import os
chunksFolder = '' #directory from which the chunks are to be loaded
def toChunks(data, location): #to convert into chunks
    pageSize = 52428800  #50MB size limit
    fileSize = os.path.getsize(location)
    if fileSize % pageSize != 1 and fileSize >= pageSize:
        reminder = fileSize % pageSize
        numChunks = fileSize // pageSize
        chunks = [data[i * pageSize:(i + 1) * pageSize] for i in range(numChunks)]
        if reminder != 0:
            chunks.append(data[fileSize - reminder:])
        return chunks
    else:
        return [data]
def fromChunks(chunkDir, outFileName): #from chunks to files
    newFile = b''
    for i in range(int(max(os.listdir(chunkDir))) + 1):
        newFile += open(f'{chunkDir}/{i}', 'rb').read()
    with open(f'{outFileName}', 'wb') as f:
        f.write(newFile)
