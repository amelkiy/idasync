from VersionsManager.VersionsManager import VersionsManager

class SingleFileManager(object):
    def __init__(self, file_name, client_id):
        self._file_name = file_name
        self._client_id = client_id
        self._unix_sock = None
        self._ver_mgr = VersionsManager.get_instance()
        
        self._init_unix_sock()
        
    def init_unix_sock(self):
        self._unix_sock = self._ver_mgr.create_client_socket(self._file_name, self._client_id)
    
    def fileno(self):
        return self._unix_sock.fileno()
        
    def get_update(self):
        self._ver_mgr.get_update(self._file_name)
        
    def update(self, data):
        self._ver_mgr.update(self._file_name, self._client_id, data)
    
    def get_all_versions(self):
        pass ###
