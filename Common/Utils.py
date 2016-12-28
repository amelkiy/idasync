from struct import pack, inpack

class Utils(object):
    @classmethod
    def recv_all(cls, sock, length):
        data = ''
        while True:
            temp = sock.recv(length - len(data))
            if temp == '':
                raise Exception("recv_all - socket error")
            data += temp
            
        return data
        
    @classmethod
    def recv_all_with_length(cls, sock):
        length = unpack("<I", cls.recv_all(sock, 4))[0]
        return cls.recv_all(sock, length)
        
    @classmethod
    def send_all_with_with_length(cls, sock, data):
        sock.sendall(pack("<I", len(data)))
        sock.sendall(data)
