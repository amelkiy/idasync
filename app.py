# Imports

from optparse import OptionParser

from Common.Consts import Consts
from Server.IdaSyncServer import IdaSyncServer

# Globals

# Functions


def main():
    parser = OptionParser()
    parser.add_option("-p", "--port",
                      dest="port",
                      help="the port to listen to communications",
                      default=Consts.DEFAULT_PORT)

    options, args = parser.parse_args()

    server = IdaSyncServer(options.port)
    server.serve_forever()

# Classes

# Main

if __name__ == '__main__':
    main()
