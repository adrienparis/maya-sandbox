import os
import shutil
import cryptography
from zipfile import ZipFile, error
import subprocess

import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding

import config
config.write("resources_path", r"C:\Users\paris_a\Documents\Creative Seeds\Atelier\Gapalion\resources")
print(config.read("resources_path"))

path_7zip = r"C:\Program Files\7-Zip\7z.exe"
# with ZipFile("drills.zip", 'w') as zipObj:
#     # Iterate over all the files in directory
#     for folderName, subfolders, filenames in os.walk(drills_path):
#         for filename in filenames:
#             #create complete filepath of file in directory
#             if filename.endswith('.pyc'):
#                 continue
#             filePath = os.path.join(folderName, filename)
#             # Add file to zip
#             zipObj.write(filePath, os.path.basename(filePath))
#     zipObj.setpassword(pwd = bytes("pswd", 'utf-8'))

def packDrills():
    rscrs_path = config.read("resources_path")
    drills_path = os.path.join(rscrs_path, "drills")
    zip_path = os.path.join(rscrs_path, "drills.zip")
    sign_path = os.path.join(rscrs_path, "drills.sign")

    key_str = config.read("private_key", secret=True)
    if key_str is not None:
        key_str = key_str.encode("utf-8")
        print(key_str)
        private_key = serialization.load_pem_private_key(
            key_str,
            password=None, backend=default_backend(),
        )
    else:
        private_key = rsa.generate_private_key(public_exponent=65537,key_size=2048,)
        key_str = private_key.private_bytes(serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption())
        config.write("private_key", key_str.decode("utf-8"), secret=True)

    # if os.path.exists("./private_key.pem"):
    #     with open("./private_key.pem", "rb") as key_file:
    #         private_key = serialization.load_pem_private_key(
    #             key_file.read(),
    #             password=None, backend=default_backend(),
    #         )
    # else:
    #     private_key = rsa.generate_private_key(public_exponent=65537,key_size=2048,)
    #     with open("private_key.pem", "w+") as f:
    #         f.write(str(private_key.private_bytes(serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption())))

    public_key = private_key.public_key()
    with open("public_key.pem", "w+") as f:
        f.write(str(public_key.public_bytes(serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)))
    
    rc = subprocess.call([path_7zip, 'a', '-y', zip_path] +
                         [drills_path])

    print("="*50)
    with open(zip_path, "rb") as m:
        message = m.read()
        prehashed = hashlib.sha256(message).hexdigest()
        prehashed = bytes(prehashed, "utf8")
        signature = private_key.sign(prehashed, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256())
        with open(sign_path, "wb+") as f:
            f.write(signature)
    


def unpackDrills():
    rscrs_path = config.read("resources_path")
    drills_path = os.path.join(rscrs_path, "drills")
    zip_path = os.path.join(rscrs_path, "drills.zip")
    sign_path = os.path.join(rscrs_path, "drills.sign")

    key_str = config.read("private_key", secret=True)
    if key_str is None:
        return
    key_str = key_str.encode("utf-8")
    private_key = serialization.load_pem_private_key(
        key_str,
        password=None, backend=default_backend(),
    )
    public_key = private_key.public_key()

    with open(sign_path, "rb") as f:
        signature = f.read()
    with open(zip_path, "rb") as m:
        message = m.read()
        prehashed = hashlib.sha256(message).hexdigest()
        prehashed = bytes(prehashed, "utf8")
    try:
        public_key.verify(signature, prehashed, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256())
        if os.path.exists('./temp'):
            shutil.rmtree('./temp')
        with ZipFile(zip_path, 'r') as zipObj:
            zipObj.extractall('./temp')
        print("Authentique")
    except cryptography.exceptions.InvalidSignature:
        print("Falcification")

def addDrillsPublisher(key):
    rscrs_path = config.read("resources_path")
    publisher_path = os.path.join(rscrs_path, "database", "publishers")
    sign_path = os.path.join(rscrs_path, "database", "publishers.sign")



# packDrills()
unpackDrills()


