# Based on:
# 	https://gist.github.com/DakuTree/98c8362fb424351b803e
# 	https://gist.github.com/jordan-wright/5770442
# 	https://gist.github.com/DakuTree/428e5b737306937628f2944fbfdc4ffc
# 	https://stackoverflow.com/questions/60416350/chrome-80-how-to-decode-cookies
# 	https://stackoverflow.com/questions/43987779/python-module-crypto-cipher-aes-has-no-attribute-mode-ccm-even-though-pycry

import os
import json
import base64
import sqlite3
from shutil import copy2, rmtree
import argparse
import hashlib
import logging
from datetime import datetime, timedelta
import csv

# python.exe -m pip install pypiwin32
import win32crypt
# python.exe -m pip install pycryptodomex
from Cryptodome.Cipher import AES


logging.basicConfig(filename='WinChromeCookieDec.log', encoding='utf-8', level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")

def hash_gen(app_path) -> tuple:
    """Generate and return sha1 and md5 as a tuple."""
    try:
        sha1 = hashlib.sha1()
        md5 = hashlib.md5()
        block_size = 65536
        with open(app_path, mode='rb') as afile:
            buf = afile.read(block_size)
            while buf:
                sha1.update(buf)
                md5.update(buf)
                buf = afile.read(block_size)
        sha1val = sha1.hexdigest()
        md5val = md5.hexdigest()
        return sha1val, md5val
    except Exception:
        logging.exception('Generating Hashes')
        return "Error", "Error"

def get_chrome_datetime(chromedate):
    """Return a `datetime.datetime` object from a chrome format datetime
    Since `chromedate` is formatted as the number of microseconds since January, 1601"""
    if chromedate != 86400000000 and chromedate:
        try:
          timestamp = datetime(1601, 1, 1) + timedelta(microseconds=chromedate)
          return timestamp.strftime("%d/%m/%Y %H:%M:%S")   
        except Exception as e:
            logging.exception(f"Error: {e}, chromedate: {chromedate}")
            return chromedate
    else:
        return ""

def DecryptChromeCookies(cookieFile, localStateFile, output = "./output", overwrite = False):
    # Create output folder
    try:
        os.mkdir(output)
    except FileExistsError as e:
        if overwrite:
            rmtree(output)
            os.mkdir(output)
        else:
            print("Output folder exists, use a different folder or --overwrite")
            logging.error("Output folder exists, use a different folder or --overwrite")
            return
    except FileNotFoundError as e:
        print("Invalid/Wrong output folder")
        logging.error("Invalid/Wrong output folder")
        return
    
    logging.info(f"Copy Cookies and Local State files from Chrome user profile to {output}")
    
    copy2(cookieFile, os.path.join(output,'Cookies'))
    copy2(cookieFile, os.path.join(output,'DecryptedCookies'))
    copy2(localStateFile, os.path.join(output,'Local State'))
    (sha1, md5) = hash_gen(os.path.join(output,'Cookies'))
    logging.info(f"Decoding cookies for file {os.path.join(output,'Cookies')} with md5 {md5} and sha1 {sha1}")
    # Load encryption key
    encrypted_key = None
    with open(os.path.join(output,'Local State'), 'r') as file:
        encrypted_key = json.loads(file.read())['os_crypt']['encrypted_key']
    encrypted_key = base64.b64decode(encrypted_key)
    encrypted_key = encrypted_key[5:]
    decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]


    # Connect to the Database
    conn = sqlite3.connect(os.path.join(output,'DecryptedCookies'))
    cursor = conn.cursor()

    # Get the results
    cursor.execute('SELECT creation_utc, expires_utc, last_access_utc, host_key, name, value, encrypted_value FROM cookies')
    for creation_utc, expires_utc, last_access_utc, host_key, name, value, encrypted_value in cursor.fetchall():
        # Decrypt the encrypted_value
        try:
            # Try to decrypt as AES (2020 method)
            cipher = AES.new(decrypted_key, AES.MODE_GCM, nonce=encrypted_value[3:3+12])
            decrypted_value = cipher.decrypt_and_verify(encrypted_value[3+12:-16], encrypted_value[-16:])
        except:
            # If failed try with the old method
            decrypted_value = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8') or value or 0
        # Update the cookies with the decrypted value
        # This also makes all session cookies persistent
        cursor.execute('\
		UPDATE cookies SET value = ?, creation_utc = ?, expires_utc = ?, last_access_utc = ?\
		WHERE host_key = ?\
		AND name = ?',
		(decrypted_value.decode(), get_chrome_datetime(creation_utc), get_chrome_datetime(expires_utc), get_chrome_datetime(last_access_utc), host_key, name));

    conn.commit()
    
    cursor.execute("SELECT * FROM cookies")
    with open(os.path.join(output,'DecryptedCookies.csv'), "w", newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=";")
        csv_writer.writerow([i[0] for i in cursor.description])
        for row in cursor.fetchall():
            csv_writer.writerow(row)

    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decrypt Chrome Cookie DB')
    parser.add_argument('-c', '--cookieDB', help='Path to Chrome Cookie DB file', default=os.getenv("APPDATA") + "/../Local/Google/Chrome/User Data/Default/Network/Cookies")
    parser.add_argument('-d', '--localState', help='Path to Chrome Local State file', default=os.getenv("APPDATA") + "/../Local/Google/Chrome/User Data/Local State")
    parser.add_argument('-o', '--output', help='Path to output', default="./output")
    parser.add_argument('-w', '--overwrite', help='Overwrite output', default=False)
    args = parser.parse_args()
    DecryptChromeCookies(args.cookieDB, args.localState, args.output, args.overwrite)