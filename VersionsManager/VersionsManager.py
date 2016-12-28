from Threading import Lock

_g_creation_lock = Lock()
_g_instance = None
_g_server

class LockedFile(Lock):
    def __init__(self):
        self.versions = {}
        self.clients = {}
        super(Lock, self).__init__()

class VersionsManager(object):
    def __init__(self):
        self._db_lock = Lock()
        self._locked_files = {}
    
    @classmethod
    def _get_instance(cls):
        global _g_creation_lock, _g_instance
        with _g_creation_lock:
            _g_instance = cls()
            
        return _g_instance
        
    def init_unix_sock(self, file_name, client_id):
        with self._db_lock:
            if file_name not in self._locked_files:
                init_file_cmd = pack("<I", INIT_FILE_CMD) + file_name
                Utils.send_all_with_length(self._client_sock, init_file_cmd)
                if Utils.recv_all(self._client_sock, 1) != '1':
                    raise Exception("Failed to initialize versions/sock file for %s", % file_name)
                
                self._locked_files[file_name] = LockedFile()
                
        with self._locked_files[file_name]:
            locked_file = self._locked_files[file_name]
            unix_sock = socket(AF_UNIX, SOCK_STREAM)
            unix_sock.connect("%s.sock" % file_name)