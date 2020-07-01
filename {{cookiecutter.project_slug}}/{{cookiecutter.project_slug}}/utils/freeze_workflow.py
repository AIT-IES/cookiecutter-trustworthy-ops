from hashlib import sha256
from json import loads as json_loads, dumps as json_dumps
from pathlib import Path

from .crypto import Crypto
from .._config import *


class FreezeWorkflow:
    '''
    Freeze the workflow.

    Create a digest of all relevant files for the worklfow.
    This digest allows to check if any file has been modified, added or deleted.
    '''

    # This glob pattern defines which files are relevant for the workflow.
    glob_patterns = [
        'environment.yml',   # main conda environment file
        'setup.py',          # main setup file
        '{{ cookiecutter.project_slug }}/**/*', # scripts and utils for running the workflow
        'workflow/**/*',     # workflow definition (Snakefile, config file, scripts, envs)
    ]

    # This pattern defines extensions for file to be excluded from the glob pattern.
    exclude_ext = [
        '.pyc' # Python byte code files (from __pycache__ subdirectories)
    ]


    def __init__( self, dir, verbose = False ):

        if not isinstance( dir, str ):
            raise TypeError( 'Input parameter "dir" has to be of type "str"' )

        if not isinstance( verbose, bool ):
            raise TypeError( 'Input parameter "verbose" has to be of type "bool"' )

        # Worflow root directory.
        self.root_dir = Path( dir ).resolve( strict = True )

        # File name for saving the file digest.
        self.freeze_file_name = Path( Path.cwd(), FREEZE_FILE_NAME ).resolve()

        # Verbosity flag.
        self.verbose = verbose

        # Helper class for decrypting / encrypting the file digest.
        self.__crypto = Crypto()


    def freeze( self ):
        '''
        Create new digest of all files relevant for the workflow.
        '''
        files_digest = {}

        # Compute digest for each file.
        for pattern in self.glob_patterns:
            glob = self.root_dir.glob( pattern )
            for g in glob:
                if g.is_file() and g.suffix not in self.exclude_ext:
                    files_digest[str( g )] = self.__sha256sum( g )

                    if self.verbose: print( 'Added file: ', g )

        # Serialize digest (convert to JSON).
        files_digest_json = json_dumps( files_digest )

        # Encrypt serialized digest.
        files_digest_encrypt = self.__crypto.encrypt( files_digest_json )

        # Write digest to file.
        with open( self.freeze_file_name, 'wb' ) as f:
            f.write( files_digest_encrypt )


    def check( self ):
        '''
        Check existing digest if files relevant for the workflow have been modified, added or deleted.
        '''
        # Open file digest.
        with open( self.freeze_file_name, 'rb' ) as f:
            files_digest_encrypt = f.read()

        # Decrypt file digest.
        try:
            files_digest_json = self.__crypto.decrypt( files_digest_encrypt )
        except RuntimeError as err:
            raise RuntimeError( 'Error opening freeze digest: {}'.format( err ) )

        # De-serialize the decrypted file digest (convert from JSON to Python object).
        files_digest_freeze = json_loads( files_digest_json )

        known_files = list( files_digest_freeze.keys() )
        unknown_files = list()
        changed_files = list()

        # Go through all files and check their status against the information from the digest.
        for pattern in self.glob_patterns:
            glob = self.root_dir.glob( pattern )
            for g in glob:
                if g.is_file() and g.suffix not in self.exclude_ext:
                
                    if str( g ) not in files_digest_freeze:
                        # File was not found in the digest.
                        unknown_files.append( str( g ) )
                        continue
                    else:
                        # Remove file from list.
                        # All files still in this list after this for-loop have 
                        # been in the stored digest, but have not been found now.
                        known_files.remove( str( g ) )

                    # Retrieve stored digest for this file.
                    freeze_digest = files_digest_freeze[str( g )]
                    
                    # Calculate current digest for this file.
                    files_digest = self.__sha256sum( g )

                    # Compare digests.
                    if not freeze_digest == files_digest:
                        # Digests disagree, the file must have been modified.
                        changed_files.append( str( g ) )
                    elif self.verbose:
                        print( 'File unchanged:', g )

        check = True

        # Print list of all changed files.
        if not 0 == len( changed_files ):
            print( '\nThe following files have been changed:' )
            for cf in changed_files:
                print( '\t{}'.format( cf ) )
            check = False
        
        # Print list of all missing files.
        if not 0 == len( known_files ):
            print( '\nThe following files are missing:' )
            for kf in known_files:
                print( '\t{}'.format( kf ) )
            check = False

        # Print list of all unknown files.
        if not 0 == len( unknown_files ):
            print( '\nThe following files have been added:' )
            for uf in unknown_files:
                print( '\t{}'.format( uf ) )
            check = False

        return check


    def __sha256sum( self, file_name ):
        h  = sha256()
        b  = bytearray( 128*1024 ) # 128kb buffer size for file hashing
        mv = memoryview( b )
        with open( file_name, 'rb', buffering = 0 ) as f:
            for n in iter( lambda : f.readinto( mv ), 0 ):
                h.update( mv[:n] )
        return h.hexdigest()