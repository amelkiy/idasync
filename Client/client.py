from thread import start_new_thread
from common.Consts import Consts
from common.utils import recv_all, send_all
from simple_json import json
import socket
import time
import traceback

# TODO: Sync mutex for all clients
# TODO: Singleton client for same process

SERVER_ADDR = "2342323"
SERVER_PORT = Consts.DEFAULT_PORT

class IdaSyncClient(object):
    DB_VERSIONS_FNAME = "db_versions.json"
    
    def __init__(self, db_name, change_callback):
        self._change_callback = change_callback
        self._sock = None
        self._version = None
        self.start_new_thread(self._input_thread)
        
    def _load_version(self):
        d = json.load(open(self.DB_VERSIONS_FNAME, "r"))
        return d[self.db_name]
            
    def _save_version(self):
        d = json.load(open(self.DB_VERSIONS_FNAME, "r"))
        d[self.db_name] = self._version
        json.dump(open(self.DB_VERSIONS_FNAME, "w"))
        
    def _send(self, data):
        send_all(self._sock, struct.pack("<I", len(data)))
        send_all(data)
    
    def _connect_server(self):
        if self._sock is not None:
            return
        sock = socket.socket()
        sock.connect((SERVER_ADDR, SERVER_PORT))
        send_all()
            
    def _input_thread(self):
        while True:
            if not sock._sock:
                time.sleep(0.1)
                continue
                
            try:
                l = struct.unpack("<I", self._sock.recv(4))[0]
                if l > 1024 * 1024:
                    raise Exception("Too long input length: %d" % l)
                data = self._sock.recv(l)
                data = json.loads(data)
                try:
                    self._change_callback(data)
                except:
                    pass
            except:
                traceback.print_exc()
                time.sleep(0.1)
        
    def submit_change(self, data):
        if not self._sock:
            self._connect()
            
        try:
            self._send(data)
        except:
            self._sock.close()
            self._sock = None
            self._connect()
            self._send(data)
            