import idaapi
import idc


class IDASyncPlugin(object):
    def __init__(self, export_callback):
        self._export_callback = export_callback

    def import_change(self, change):
        print '[*] Got change! %s(%s, %s)' % (change.func, ','.join(map(str, change.args)), ','.join(['%s=%s' % (k, v) for k, v in change.kwargs.items()]))
        getattr(idc, change.func)(*change.args, **change.kwargs)