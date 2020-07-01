from pathlib import Path
from stat import S_IREAD, S_IWRITE


class FilePermissions:
    '''
    Helper class for restricting the permissions for certain files to read and write access
    for the current user only.
    '''

    def __init__( self ):
        pass

    def restrict_access( self, file ):
        '''
        Restrict permissions for a file to read and write access for the current user only.
        '''
        if not isinstance( file, Path ):
            raise TypeError( 'Input parameter "file" has to be of type "pathlib.Path"' )

        if not file.is_file():
            raise RuntimeError( 'Not a file:', file )

        # Set file permissions
        file.chmod( S_IREAD | S_IWRITE )
