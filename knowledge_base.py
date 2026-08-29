"""
knowledge base update service
"""
import os

import config_data
import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def check_md5(md5_str: str):
    """
    check if the md5 value exists in the md5.txt file, if not, create the file and return False, if exists, return True
    """
    if not os.path.exists(config.md5_path):
        # if path not exist then create the respective md5 code and return False
        open(config.md5_path, "w", encoding="utf-8").close()
        return False
    else:
        for line in open(config.md5_path, "r", encoding="utf-8").readlines():
            # strip space and newline character
            line = line.strip()
            if line == md5_str:
                return True

        return False


def save_md5(md5_str: str):
    """
    save the md5 value to the md5.txt file
    """
    # with keyword can open and close the file automatically, and the file will be closed when the code block is exited
    # "a" stands for append mode, which means that the new content will be added to the end of the file, and if the file does not exist, it will be created
    with open(config.md5_path, "a", encoding="utf-8") as f:
        f.write(md5_str + "\n")


def get_string_md5(input_str: str, encoding='utf-8'):
    """
    convert the input string to md5 value
    """

    # 1st convert string into bytes list
    str_byte = input_str.encode(encoding=encoding)

    # create md5 object
    md5_obj = hashlib.md5()  # get md5 obj
    md5_obj.update(str_byte)  # update content(pass the bytes list to be converted)
    md5_hex = md5_obj.hexdigest()  # get the md5 hex string(16 hex string)

    return md5_hex


class KnowledgeBaseService(object):
    def __init__(self):
        # if the folder not exits then create it, if exists then skip
        os.makedirs(config.persist_directory, exist_ok=True)

        # vector store instance, Chroma vector database object
        self.chroma = Chroma(
            collection_name=config.collection_name,  # collection name, similar to table name in database
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.persist_directory,  # specify the folder where data is stored
        )

        # text splitter instance, RecursiveCharacterTextSplitter object
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,  # maximum length of the split text segment
            chunk_overlap=config.chunk_overlap,  # overlap length of the split text segment
            separators=config.separators,  # natural paragraph split symbols
            length_function=len,  # use Python's built-in len function as the basis for length statistics
        )

    def upload_by_str(self, data: str, filename):
        """
            convert the input string to vector and store it in the vector database
            """
        # get the md5 value of the input string
        md5_hex = get_string_md5(data)

        if check_md5(md5_hex):
            return "The md5 value already exists, the data has been processed, and the data will not be processed again."

        if len(data) > config_data.max_split_char_number:
            knowledge_chunks: list = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]

        metadata = {
            "source": filename,
            # 2025-01-01 10:00:00
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "tester",
        }

        self.chroma.add_texts(  # add content to vector db table
            # iterable -> list \ tuple
            knowledge_chunks,
            metadata=[metadata for _ in knowledge_chunks],
        )

        # save md5
        save_md5(md5_hex)

        return "[succeed]content has been loaded in vector storage."


if __name__ == "__main__":
    service = KnowledgeBaseService()
    r = service.upload_by_str("test2", "testfile")
    print(r)
