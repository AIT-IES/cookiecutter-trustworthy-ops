from getpass import getpass
from json import loads as json_loads, dumps as json_dumps
from pathlib import Path

from .crypto import Crypto
from .file_permissions import FilePermissions
from .._config import *


class CredentialsCache:
    '''
    Store credentials needed for the workflow in an encrypted cache.

    Returns a singleton instance of the credentials cache implementation.
    '''

    # Singleton instance.
    __instance = None

    def __new__( cls, new_cache = False ):

        if CredentialsCache.__instance is None:
            CredentialsCache.__instance = CredentialsCacheImpl( new_cache )

        return CredentialsCache.__instance


class CredentialsCacheImpl:
    '''
    Implementation of the credentials cache.
    '''

    def __init__( self, new_cache = False ):

        if not isinstance( new_cache, bool ):
            raise TypeError( 'Input parameter "new_cache" has to be of type "bool"' )

        # Set filename for cache file.
        self.cache_file_name = Path( Path.cwd(), CREDENTIALS_CACHE_FILE_NAME ).resolve()

        # Delete old cache file if requested.
        if self.cache_file_name.is_file() and new_cache:
            if self.__user_select( 'Delete old password cache? [Y/n] ' ):
               self.cache_file_name.unlink()

        # Helper class for encrypting / decrypting data.
        self.__crypto = Crypto()

        # Helper class for setting file permissions.
        self.__file_permissions = FilePermissions()

        # Load data from cache file if available.
        if self.cache_file_name.is_file():
            try:
                with open( self.cache_file_name, 'rb' ) as f:
                    encrypted_content = f.read()
                    serialized_content = self.__crypto.decrypt( encrypted_content )
                    self.__db = json_loads( serialized_content )

            except RuntimeError as err:
                raise RuntimeError( 'Error opening credential cache: {}'.format( err ) )
        else:
            self.__db = { 'sitenames' : [] }


    def retrieve( self, sitename ):
        '''
        Retrieve the credentials for a given site from the cache.

        :return: tuple with user name and password
        '''
        # Check if credentials have been stored for this site.
        if not sitename in self.__db['sitenames']:
            raise RuntimeError( 'Unknown sitename: "{}"'.format( sitename ) )

        # Retrieve user name from cache.
        key = '{}_user'.format( sitename )
        value = self.__db[key]
        user = self.__crypto.decrypt( value )

        # Retrieve password from cache.
        key = '{}_pwd'.format( sitename )
        value = self.__db[key]
        pwd = self.__crypto.decrypt( value )

        return ( user, pwd )


    def store( self, sitename ):
        '''
        Store the credentials for a given site to the cache.

        :return: none
        '''
        # Check if site is already known.
        if sitename in self.__db['sitenames']:
            # Cache already has credentials stored for this site.
            # Ask user if they should be overwritten.
            if not self.__user_select( 'Overwrite existing credentials for "{}"? [Y/n] '.format( sitename ) ):
                return
        else:
            # Cache already has no credentials stored for this site yet.
            # Add site to list of known sites.
            self.__db['sitenames'].append( sitename )
            print( 'Please enter credentials for "{}":'.format( sitename ) )

        # Encrypt and store username.
        key = '{}_user'.format( sitename )
        value = getpass( 'User name:' )
        self.__db[key] = self.__crypto.encrypt( value ).decode('utf-8')
        del value

        # Encrypt and store password.
        key = '{}_pwd'.format( sitename )
        value = getpass( 'Password:' )
        self.__db[key] = self.__crypto.encrypt( value ).decode('utf-8')
        del value

        # Store cache.
        with open( self.cache_file_name, 'wb' ) as f:
            serialized_content = json_dumps( self.__db )
            encrypted_content = self.__crypto.encrypt( serialized_content )
            f.write( encrypted_content )

        # Set cache file permissions.
        self.__file_permissions.restrict_access( self.cache_file_name )


    def sitenames( self ):
        '''
        Retrieve list of sites for which credentials have been stored.

        :return: list of known sitenames
        '''
        return self.__db['sitenames']


    def __user_select( self, question ):
        while True:
            # Prompt user for confirmation (yes/no).
            choice = input( question ).lower()
            if choice in [ 'yes', 'y', '' ]:
                return True
            elif choice in [ 'no','n' ]:
                return False
            else:
                print( 'Please respond with "yes" or "no"' )

