from thread import start_new_thread
from ..Commmon.Utils import Utils

class IdaSyncClient(object):
    def __init__(self, sock, client_id):
        self._sock = sock
        self._file_name = None
        self._client_id = None
        self._file_manager = None

    @classmethod
    def start_threaded(cls, sock, client_id):
        start_new_thread(cls._run, (sock.dup(), client_id))

    @classmethod
    def _run(cls, sock, client_id):
        # This runs in a new thread
        IdaSyncClient(sock, client_id).start()

    def start(self):
        self._init_client()
        
        while True:
            rdfs, _, _ = select([self._sock, self._file_manager], [], [])
            if self._sock in rdfs:
                data = self._get_client_update()
                self._update_server(data)
                
            if self._file_manager in rdfs:
                data = self._get_server_update()
                self._update_client(data)
                
    def _init_client(self):
        data = Utils.recv_all_with_length(self._sock)
        # ...
        
        self._file_manager = SingleFileManager(self._file_name, self._client_id)
        versions = self._file_manager.get_all_versions()
        for ver_num, data in versions.iteritems():
            self._update_client({ver_num: data})
        
    def _get_client_update(self):
        return json.laods(Utils.recv_all_with_length(self._sock))
        
    def _get_server_update(self):
        return self._file_manager.get_update()
        
    def _update_client(self, data):
        Utils.send_all_with_with_length(self._sock, json.dumps(data))
    
    def _update_server(self, data):
        self._file_manager.update(data)
