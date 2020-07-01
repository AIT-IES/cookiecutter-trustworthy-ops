from base64 import b64encode, b64decode
from getpass import getpass
from hashlib import sha256
from os import environ
from Crypto import Random
from Crypto.Cipher import AES

from .._config import *


class Crypto:
    '''
    Helper class for encrypting and decrypting data.
    
    Asks for user-defined password when instantiated.
    There are 2 options for providing this password:
      1. By default, the user is asked to type in the password in the command line.
      2. The user can set an environment variable called '{{ cookiecutter.project_slug | upper }}_PWD_FILE',
         which has to point to a file containing the password. The user is responsible
         to set secure file permissions (i.e., read access for the user ONLY). This
         option is intended for automated execution.

    Returns a singleton instance of the crypto implementation.
    '''

    # Singleton instance.
    __instance = None

    def __new__( cls ):

        if Crypto.__instance is None:
            Crypto.__instance = CryptoImpl()

        return Crypto.__instance


class CryptoImpl:
    '''
    Simple crypto implementation using an AES cipher (CBC mode).

    Inspired by: https://stackoverflow.com/a/12525165
    '''

    def __init__( self ):

        # Check for credentials (defined via environment
        # variable) or ask user for a secret passphrase.
        if '{{ cookiecutter.project_slug | upper }}_PWD_FILE' in environ:
            cred_file_name = Path( environ['{{ cookiecutter.project_slug | upper }}_PWD_FILE'] )
            with open( cred_file_name, 'r' ) as f:
                user_key = f.read()
        else:
            user_key = getpass( 'Enter your secret passphrase:' )

        # Store passphrase as key for cipher.
        self.__key = sha256( user_key.encode() ).digest()

        # Store cipher block size.
        self.__bs = AES.block_size


    def encrypt( self, plaintext ):
        '''
        Encrypt plaintext.

        :return: encrypted data as sequence of bytes
        '''
        # Pad plaintext.
        raw = self.__pad( plaintext )

        # Initialise cipher randomly.
        iv = Random.new().read( self.__bs )

        # Create cipher.
        cipher = AES.new( self.__key, AES.MODE_CBC, iv )

        # Encrypt.
        return b64encode( iv + cipher.encrypt( raw.encode() ) )


    def decrypt( self, ciphertext ):
        '''
        Decrypt ciphertext.

        :return: decrypted data as string
        '''
        try:
            # Decode ciphertext.
            enc = b64decode( ciphertext )

            # Create cipher.
            cipher = AES.new( self.__key, AES.MODE_CBC, enc[:self.__bs] )

            # Decrypt.
            dec = cipher.decrypt( enc[self.__bs:] )

            # Depad and decode.
            return self.__unpad( dec ).decode( 'utf-8' )

        except Exception as e:
            #print( e )
            raise RuntimeError( 'Decryption failed.' )


    def __pad( self, s ):
        l = self.__bs - len( s ) % self.__bs
        return s + l * chr( l )


    def __unpad( self, s ):
        return s[:-ord( s[len( s )-1:] )]
