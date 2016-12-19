import idaapi
import idc


class Change(object):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return '%s(%s, %s)' % (self.func, ','.join(map(str, self.args)), ','.join(['%s=%s' % (k, v) for k, v in self.kwargs.items()]))


class IDASyncIDPHooks(idaapi.IDP_Hooks):
    def __init__(self, plugin):
        super(IDASyncIDPHooks, self).__init__()
        self._plugin = plugin

    def renamed(self, ea, new_name, local_name):
        self._plugin.send_change(Change("MakeName", ea, new_name))


class IDASyncPlugin(object):
    def __init__(self, export_callback):
        self._export_callback = export_callback
        self._idp_hooks = IDASyncIDPHooks(self)

    def start(self):
        self._idp_hooks.hook()

    def end(self):
        self._idp_hooks.unhook()

    def import_change(self, change):
        change = Change(change.func, *change.args, **change.kwargs)

        print '[*] Got change! %s' % repr(change)
        getattr(idc, change.func)(*change.args, **change.kwargs)

    def send_change(self, change):
        print '[*] Send change! %s' % repr(change)
        try:
            pass
        except e:
            Warning(e.message)