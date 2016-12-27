from thread import start_new_thread
import threading
from ..Common.Consts import Consts
from ..Common.utils import Utils
import simplejson as json
import socket
import time
import traceback
import ssl
import os

# TODO: Sync mutex for all clients
# TODO: Singleton client for same process

SERVER_ADDR = "2342323"
SERVER_PORT = Consts.DEFAULT_PORT

class IdaSyncClient(object):
    DB_VERSIONS_FNAME = "db_versions.json"
    s_instance = None
    
    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls.s_instance is None:
            cls(*args, **kwargs)
        return cls.s_instance
    
    def __init__(self, db_name, change_callback):
        if self.s_instance is not None:
            raise Exception("Cannot create more than one instance of IdaSyncClient")
        else:
            self.s_instance = self
            
        self._change_callback = change_callback
        self._sock = None
        self._version = None
        self._cached_msg_ids = {}
        
        self._load_version()
        self._lock = threading.RLock()
        start_new_thread(self._input_thread, ())
        
    def _load_version(self):
        if not os.path.isfile(self.DB_VERSIONS_FNAME):
            self._version = 0
        else:
            d = json.load(open(self.DB_VERSIONS_FNAME, "r"))
            self._version = d[self.db_name]
            
    def _save_version(self):
        d = json.load(open(self.DB_VERSIONS_FNAME, "r"))
        d[self.db_name] = self._version
        json.dump(open(self.DB_VERSIONS_FNAME, "w"))
        
    def _send(self, data):
        if isinstance(data, dict):
            data = json.dumps(data)
        Utils.send_all_with_length(self._sock, data)
        
    def _disconnect_server(self):
        self._lock.acquire()
        try:
            if self._sock is None:
                return
            self._sock.close()
        except:
            pass
        finally:
            self._sock = None
            self._lock.release()
    
    def _connect_server(self):
        self._lock.acquire()
        try:
            if self._sock is not None:
                return
            sock = socket.socket()
            sock.settimeout(10.0)
            sock.connect((SERVER_ADDR, SERVER_PORT))
            sock.settimeout(None)
            sock = ssl.wrap_socket(sock)
            self._sock = sock
            self._send({"db_name": self._db_name, "version": self._version})
        except:
            self._disconnect_server()
            traceback.print_exc()
        finally:
            self._lock.release()
            
    def _input_thread(self):
        while True:
            self._connect_server()
            if not self._sock:
                time.sleep(1.0)
                continue
                
            try:
                data = Utils.recv_all_with_length(self._sock)
                msg = json.loads(data)
                msg_id = msg["id"]
                data = msg["data"]
            except:
                self._disconnect_server()
                traceback.print_exc()
                time.sleep(0.1)
                continue
            print "Got update message: %s" % str(data)
            if msg_id in self._cached_msg_ids:
                print "\tSkipping"
                continue
            self._change_callback(data)
            self._cached_msg_ids[msg_id] = None
            self._version += 1
            self._save_version()
            print "\tNew version: %d"
                
        
    def submit_change(self, data):
        # Only the input thread calls connect_server()
        msg_id = os.urandom(16)
        msg = {"id": msg_id.encode("hex"), "data": data}
            
        try:
            self._send(msg)
            self._cached_msg_ids[msg_id] = None
        except:
            self._disconnect_server()
            time.sleep(2.0)
            self._send(data)
            