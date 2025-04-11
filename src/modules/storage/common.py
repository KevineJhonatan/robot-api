import os


async def verify_file_exist(file):
    return os.path.isfile(file)

async def VerifyIfDirExistElseCreate(dir : str):
    if not os.path.isdir(dir):
        os.makedirs(dir)

async def VerifyIfDirExist(dir : str):
    return os.path.isdir(dir)

async def save_file(path, file, content):
    await VerifyIfDirExistElseCreate(path)
    with open(file, mode="wb") as file:
        file.write(content)

