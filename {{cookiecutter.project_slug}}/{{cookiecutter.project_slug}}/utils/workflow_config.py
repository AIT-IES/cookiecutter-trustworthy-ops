from json import load as json_load
from pathlib import Path

from .._config import CONFIG_FILE_NAME


class WorkflowConfig:
    '''
    Helper class for retrieving information from the workflow configuration.
    '''

    def __init__( self, root_dir ):
        self.__file_path = Path( root_dir, CONFIG_FILE_NAME ).resolve( strict = True )

        with open( self.__file_path ) as f:
            self.__config = json_load( f )


    def file_path( self ):
        '''
        Get path to workflow configuration file.
        '''
        return self.__file_path


    def get( self, attr ):
        '''
        Retrieve an attribute from the workflow configuration by attribute key.
        '''
        if attr in self.__config:
            return self.__config[attr]
        else:
            raise RuntimeError( 'Attribute "{}" missing in workflow configuration!'.format( attr ) )


    def num_cores( self ):
        '''
        Retrieve "num_cores" attribute from the workflow configuration.
        '''
        return self.get( 'num_cores' )


    def credentials( self ):
        '''
        Retrieve "credentials" attribute from the workflow configuration.
        '''
        return self.get( 'credentials' )


    def target( self ):
        '''
        Retrieve "target" attribute from the workflow configuration.
        '''
        return self.get( 'target' )


    def run_id_format( self ):
        '''
        Retrieve "run_id_format" attribute from the workflow configuration.
        '''
        return self.get( 'run_id_format' )
