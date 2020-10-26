# instrument.py, base class to implement instrument objects
# Reinier Heeres <reinier@heeres.eu>, 2008
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import types
import copy
import time
import math
import inspect
import numpy as np
import logging

try:
    from lib.config import get_config
    config = get_config()
except:
    config = dict()

try:
    import objectsharer as objsh
except ImportError:
    pass

TYPE_INSTRUMENT = 'ins'

def timeout_add(delay, func, *args):
    try:
        return objsh.helper.backend.timeout_add(delay, func, *args)
    except:
        return -1

class Instrument(object):
    """
    Base class for instruments.

    Usage:
    Instrument.get(<variable name or list>)
    Instrument.set(<variable name or list>)

    Implement an instrument:
    In __init__ call self.add_variable(<name>, <option dict>)
    Implement _do_get_<variable> and _do_set_<variable> functions
    """

    # FLAGS are used to to set extra properties on a parameter.

    FLAG_GET = 0x01             # Parameter is gettable
    FLAG_SET = 0x02             # {arameter is settable
    FLAG_GETSET = 0x03          # Shortcut for GET and SET
    FLAG_GET_AFTER_SET = 0x04   # perform a 'get' after a 'set'
    FLAG_SOFTGET = 0x08         # 'get' operation is simulated in software,
                                # e.g. an internally stored value is returned.
                                # Only use for parameters that cannot be read
                                # back from a device.
    FLAG_PERSIST = 0x10         # Write parameter to config file if it is set,
                                # try to read again for a new instance

    USE_ACCESS_LOCK = False     # For now

    RESERVED_NAMES = ('name', 'type')

    def __init__(self, name, **kwargs):
        self._name = name
        self._initialized = False
        self._locked = False
        self._remove_cb = None
        self._instruments = None

        self._changed = {}
        self._changed_hid = None

        self._options = kwargs
        if 'tags' not in self._options:
            self._options['tags'] = []

        self._parameters = {}
        self._parameter_groups = {}
        self._functions = {}
        self._added_methods = []
        self._probe_ids = []
        self._set_order = None

        self._default_read_var = None
        self._default_write_var = None

        # Info for auxiliary parameters
        self._aux_info = dict()

    def __str__(self):
        return "Instrument '%s'" % (self.get_name())

    # Note that in python there is no guarantee that this will be called!
    def __del__(self):
        self.close()

    # It is much safer to use the "with a as ins:" clause
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        '''Override to release instrument resources.'''
        pass

    def set_remove_cb(self, cb):
        self._remove_cb = cb

    def remove(self):
        if self._remove_cb:
            self._remove_cb()

    def set_instruments(self, val):
        '''Called by instrument_server to set instruments object.'''
        self._instruments = val

    def get_instruments(self):
        '''Return the instruments object.'''
        return self._instruments

    def get_name(self):
        '''Return the name of the instrument as a string.'''
        return self._name

    def get_type(self):
        '''Return type of instrument as a string.'''
        modname = str(self.__module__)
        return modname

    def get_options(self):
        '''Return instrument options.'''
        return self._options

    def get_tags(self):
        '''Return an array of tags.'''
        return self._options['tags']

    def add_tag(self, tag):
        '''Add a tag to the tag list.'''
        self._options['tags'].append(tag)

    def has_tag(self, tags):
        '''Return whether instrument has any tag in 'tags'.'''
        if type(tags) not in (types.ListType, types.TupleType):
            tags = (tags,)
        for tag in tags:
            if tag in self._options['tags']:
                return True
        return False

    def _add_options_to_doc(self, options):
        doc = options.get('doc', '')

        if 'option_list' in options:
            doc += '\n\nAllowed parameters:\n'
            for fmtval in options['option_list']:
                doc += '    %s\n' % str(fmtval)
        if 'format_map' in options:
            doc += '\n\nAllowed parameters:\n'
            for fmtkey, fmtval in options['format_map'].iteritems():
                doc += '    %s or %s\n' % (fmtkey, fmtval)

        if doc != '':
            options['doc'] = doc

    def add_parameter(self, name, **kwargs):
        '''
        Create an instrument 'parameter' that is known by the whole
        environment (gui etc).

        This function creates the 'get_<name>' and 'set_<name>' wrapper
        functions that will perform checks on parameters and finally call
        '_do_get_<name>' and '_do_set_<name>'. The latter functions should
        be implemented in the instrument driver.

        Input:
            name (string): the name of the parameter (string)
            optional keywords:
                type: types.FloatType, types.StringType, etc.
                flags: bitwise or of Instrument.FLAG_ constants.
                    If not set, FLAG_GETSET is default
                channels: tuple. Automagically create channels, e.g.
                    (1, 4) will make channels 1, 2, 3, 4.
                minval, maxval: values for bound checking
                units (string): units for this parameter
                maxstep (float): maximum step size when changing parameter
                stepdelay (float): delay when setting steps (in milliseconds)
                tags (array): tags for this parameter
                doc (string): documentation string to add to get/set functions
                format_map (dict): map describing allowed options and the
                    formatted (mostly GUI) representation
                option_list (array/tuple): allowed options
                persist (bool): if true load/save values in config file
                probe_interval (int): interval in ms between automatic gets
                listen_to (list of (ins, param) tuples): list of parameters
                    to watch. If any of them changes, execute a get for this
                    parameter. Useful for a parameter that depends on one
                    (or more) other parameters.

        Output: None
        '''

        if name in self._parameters:
            logging.error('Parameter %s already exists.', name)
            return
        elif name in self.RESERVED_NAMES:
            logging.error("'%s' is a reserved name, not adding parameter",
                    name)
            return

        options = kwargs
        if 'flags' not in options:
            options['flags'] = Instrument.FLAG_GETSET
        if 'type' not in options:
            options['type'] = types.NoneType
        if 'tags' not in options:
            options['tags'] = []

        # If defining channels call add_parameter for each channel
        if 'channels' in options:
            if len(options['channels']) == 2 and type(options['channels'][0]) is types.IntType:
                minch, maxch = options['channels']
                channels = xrange(minch, maxch + 1)
            else:
                channels = options['channels']

            for i in channels:
                chopt = copy.copy(options)
                del chopt['channels']
                chopt['channel'] = i
                chopt['base_name'] = name

                if 'channel_prefix' in options:
                    var_name = options['channel_prefix'] % i + name
                else:
                    var_name = '%s%s' % (name, i)

                self.add_parameter(var_name, **chopt)

            return

        self._parameters[name] = options

        if 'channel' in options:
            ch = options['channel']
        else:
            ch = None

        base_name = kwargs.get('base_name', name)

        if options['flags'] & Instrument.FLAG_GET:
            if ch is not None:
                func = lambda query=True, **lopts: \
                    self.get(name, query=query, channel=ch, **lopts)
            else:
                func = lambda query=True, **lopts: \
                    self.get(name, query=query, **lopts)

            self._add_options_to_doc(options)
            func.__doc__ = 'Get variable %s' % name
            if 'doc' in options:
                func.__doc__ += '\n%s' % options['doc']

            setattr(self, 'get_%s' % name,  func)
            self._added_methods.append('get_%s' % name)

            # Set function to do_get_%s or _do_get_%s, whichever is available
            # (if no function specified)
            if 'get_func' not in options:
                options['get_func'] = getattr(self, 'do_get_%s' % base_name, \
                    getattr(self, '_do_get_%s' % base_name, None))
            if options['get_func'] is not None:
                if options['get_func'].__doc__ is not None:
                    func.__doc__ += '\n%s' % options['get_func'].__doc__
            else:
                options['get_func'] = lambda *a, **kw: \
                    self._get_not_implemented(base_name)
                self._get_not_implemented(base_name)

        if options['flags'] & Instrument.FLAG_SOFTGET:
            if ch is not None:
                func = lambda query=True, **lopts: \
                    self.get(name, query=False, channel=ch, **lopts)
            else:
                func = lambda query=True, **lopts: \
                    self.get(name, query=False, **lopts)

            func.__doc__ = 'Get variable %s (internal stored value)' % name
            setattr(self, 'get_%s' % name,  func)
            self._added_methods.append('get_%s' % name)

        if options['flags'] & Instrument.FLAG_SET:
            if ch is not None:
                func = lambda val, **lopts: self.set(name, val, channel=ch, **lopts)
            else:
                func = lambda val, **lopts: self.set(name, val, **lopts)

            func.__doc__ = 'Set variable %s' % name
            if 'doc' in options:
                func.__doc__ += '\n%s' % options['doc']
            setattr(self, 'set_%s' % name, func)
            self._added_methods.append('set_%s' % name)

            # Set function to do_set_%s or _do_set_%s, whichever is available
            # (if no function specified)
            if 'set_func' not in options:
                options['set_func'] = getattr(self, 'do_set_%s' % base_name, \
                    getattr(self, '_do_set_%s' % base_name, None))
            if options['set_func'] is not None:
                if options['set_func'].__doc__ is not None:
                    func.__doc__ += '\n%s' % options['set_func'].__doc__
            else:
                if not options['flags'] & Instrument.FLAG_SOFTGET:
                    options['set_func'] = lambda *a, **kw: \
                        self._set_not_implemented(base_name)
                    self._set_not_implemented(base_name)
                else:
                    options['set_func'] = lambda *a, **kw: None

        if options['flags'] & self.FLAG_PERSIST:
            val = config.get('persist_%s_%s' % (self._name, name))
            options['value'] = val
        elif 'value' not in options:
            options['value'] = None

        if 'probe_interval' in options:
            interval = int(options['probe_interval'])
            self._probe_ids.append(timeout_add(interval,
                lambda: self.get(name)))

        if 'listen_to' in options:
            insset = set([])
            inshids = []
            for (ins, param) in options['listen_to']:
                inshids.append(ins.connect('changed', \
                        self._listen_parameter_changed_cb,
                        param, options['get_func']))
            options['listed_hids'] = inshids

        if 'group' in options:
            g = options['group']
            if g not in self._parameter_groups:
                self._parameter_groups[g] = [name]
            else:
                self._parameter_groups[g].append(name)

        self.emit('parameter-added', name)

    def remove_parameter(self, name):
        '''Remove parameter <name>.'''

        if name not in self._parameters:
            return

        for func in ('get_%s' % name, 'set_%s' % name):
            if hasattr(self, func):
                delattr(self, func)

        del self._parameters[name]
        self.emit('parameter-removed', name)

    def has_parameter(self, name):
        '''Return whether instrument has a parameter called 'name'.'''
        return (name in self._parameters)

    def get_parameter_options(self, name):
        '''
        Return list of options for paramter.

        Input: name (string)
        Output: dictionary of options
        '''
        if self._parameters.has_key(name):
            return self._parameters[name]
        else:
            return None

    def get_shared_parameter_options(self, name):
        '''
        Return list of options for paramter.

        Input: name (string)
        Output: dictionary of options
        '''
        if self._parameters.has_key(name):
            options = dict(self._parameters[name])
            for i in ('get_func', 'set_func'):
                if i in options:
                    del options[i]
            if 'type' in options and options['type'] is types.NoneType:
                options['type'] = None
            return options
        else:
            return None

    def set_parameter_options(self, name, **kwargs):
        '''
        Change parameter options.

        Input:  name of parameter (string)
        Ouput:  None
        '''
        if name not in self._parameters:
            print 'Parameter %s not defined' % name
            return None

        for key, val in kwargs.iteritems():
            self._parameters[name][key] = val

        self.emit('parameter-changed', name)

    def get_parameter_tags(self, name):
        '''
        Return tags for parameter 'name'.

        Input:  name of parameter (string)
        Ouput:  array of tags
        '''

        if name not in self._parameters:
            return []

        return self._parameters[name]['tags']

    def add_parameter_tag(self, name, tag):
        '''
        Add tag to list of tags for parameter 'name'.

        Input:  (1) name of parameter (string)
                (2) tag (string)
        Ouput:  None
        '''

        if name not in self._parameters:
            return

        self._parameters[name]['tags'].append(tag)

    def set_parameter_bounds(self, name, minval, maxval):
        '''
        Change the bounds for a parameter.

        Input:  (1) name of parameter (string)
                (2) minimum value
                (3) maximum value
        Output: None
        '''
        self.set_parameter_options(name, minval=minval, maxval=maxval)

    def set_channel_bounds(self, name, channel, minval, maxval):
        '''
        Change the bounds for a channel.

        Input:  (1) name of parameter (string)
                (2) channel number (int)
                (3) minimum value
                (4) maximum value
        Output: None
        '''

        opts = self.get_parameter_options(name)
        if 'channel_prefix' in opts:
            var_name = opts['channel_prefix'] % channel + name
        else:
            var_name = '%s%d' % (name, channel)

        self.set_parameter_options(var_name, minval=minval, maxval=maxval)

    def set_parameter_rate(self, name, stepsize, stepdelay):
        '''
        Change the rate properties for a channel.

        Input:
            stepsize (float): the maximum step size
            stepdelay (float): the delay after each step
        Output:
            None
        '''
        self.set_parameter_options(name, maxstep=stepsize, stepdelay=stepdelay)

    def get_parameter_names(self):
        '''
        Returns a list of parameter names.

        Input: None
        Output: all the paramter names (list of strings)
        '''
        return self._parameters.keys()

    def get_parameters(self):
        '''
        Return the parameter dictionary.

        Input: None
        Ouput: Dictionary, keys are parameter names, values are the options.
        '''
        return self._parameters

    def get_pickleable_parameters(self):
        '''
        Return the parameter dictionary without things we can't pickle, like function
        objects.
        '''
        _p = copy.deepcopy(self._parameters)
        for key in _p:
            _p[key].pop('set_func', None)
            _p[key].pop('get_func', None)
        return _p


    def get_parameter_values(self, query=False):
        '''
        Return a dictionary of parameter -> value
        '''
        ret = {p: self.get(p, query=query) for p in self._parameters.keys()}
        return ret

    def get_shared_parameters(self):
        '''
        Return the parameter dictionary, with non-shareable items stripped.

        Input: None
        Ouput: Dictionary, keys are parameter names, values are the options.
        '''

        params = {}
        for key in self._parameters:
            params[key] = self.get_shared_parameter_options(key)
        return params

    def get_parameter_groups(self):
        '''
        Return a dictionary with parameter group name -> group members.
        '''
        return self._parameter_groups

    def set_set_order(self, order):
        '''
        The set order specifies the order in which to set parameters if set is
        called with a dictionary. Useful when restoring previous parameters.
        '''
        self._set_order = order

    def get_set_order(self):
        return self._set_order

    def format_parameter_value(self, param, val):
        '''
        Format a string for value <val> of parameter <param>.
        '''

        opt = self.get_parameter_options(param)

        try:
            if 'format_function' in opt:
                valstr = opt['format_function'](val)
            elif 'format_map' in opt:
                valstr = opt['format_map'][val]
            else:
                if 'format' in opt:
                    format = opt['format']
                else:
                    format = '%s'

                if type(val) in (types.ListType, types.TupleType):
                    val = tuple(val)

                elif type(val) is types.DictType:
                    fmt = ""
                    first = True
                    for k in val.keys():
                        if first:
                            fmt += '%s: %s' % (k, format)
                            first = False
                        else:
                            fmt += ', %s: %s' % (k, format)
                    format = fmt
                    val = tuple(val.values())

                elif val is None:
                    val = ''

                valstr = format % (val)

        except Exception, e:
            valstr = str(val)

        if 'units' in opt:
            unitstr = ' %s' % opt['units']
        else:
            unitstr = ''

        return '%s%s' % (valstr, unitstr)

    def format_range(self, param):
        '''
        Format the range allowed for parameter <param>
        '''

        popts = self.get_parameter_options(param)
        text = ''
        if 'minval' in popts or 'maxval' in popts:

            if 'format' in popts:
                format = popts['format']
            else:
                format = '%s'

            text = '['
            if 'minval' in popts:
                text += format % popts['minval']
            text += ' : '
            if 'maxval' in popts:
                text += format % popts['maxval']
            text += ']'

        return text

    def format_rate(self, param):
        '''
        Format the rate allowed for parameter <param>
        '''

        popts = self.get_parameter_options(param)
        text = ''
        if 'maxstep' in popts and popts['maxstep'] is not None:
            text += '%s' % popts['maxstep']
            if 'stepdelay' in popts and popts['stepdelay'] is not None:
                text += ' / %sms' % popts['stepdelay']
            else:
                text += ' / 100ms'

        return text

    def _get_value(self, name, query=True, **kwargs):
        '''
        Private wrapper function to get a value.

        Input:  (1) name of parameter (string)
                (2) query the instrument or return stored value (Boolean)
                (3) optional list of extra options
        Output: value of parameter (whatever type the instrument driver returns)
        '''

        try:
            p = self._parameters[name]
        except:
            print 'Could not retrieve options for parameter %s' % name
            return None

        if 'channel' in p and 'channel' not in kwargs:
            kwargs['channel'] = p['channel']

        flags = p['flags']
        if not query or flags & 8: #self.FLAG_SOFTGET:
            if 'value' in p:
                if p['type'] == np.ndarray:
                    return np.array(p['value'])
                else:
                    return p['value']
            else:
#                logging.debug('Trying to access cached value, but none available')
                return None

        # Check this here; getting of cached values should work
        if not flags & 1: #Instrument.FLAG_GET:
            print 'Instrument does not support getting of %s' % name
            return None

        if 'base_name' in p:
            base_name = p['base_name']
        else:
            base_name = name

        func = p['get_func']
        value = func(**kwargs)
        if 'type' in p and value is not None:
            try:
                if p['type'] == types.IntType:
                    value = int(value)
                elif p['type'] == types.FloatType:
                    value = float(value)
                elif p['type'] == types.ComplexType:
                    value = complex(value)
                elif p['type'] == types.StringType:
                    pass
                elif p['type'] == types.BooleanType:
                    try:
                        value = bool(int(value))
                    except ValueError:
                        value = bool(value)
                elif p['type'] == types.NoneType:
                    pass
                elif p['type'] == np.ndarray:
                    value = np.array(value)
            except:
                logging.warning('Unable to cast value "%s" to %s', value, p['type'])

        p['value'] = value
        return value

    def get(self, name, query=True, fast=False, **kwargs):
        '''
        Get one or more Instrument parameter values.

        Input:
            name (string or list/tuple of strings): name of parameter(s)
            query (bool): whether to query the instrument or return the
                last stored value
            fast (bool): if True perform as fast as possible, e.g. don't
                emit a signal to update the GUI.
            kwargs: Optional keyword args that will be passed on.

        Output: Single value, or dictionary of parameter -> values
                Type is whatever the instrument driver returns.
        '''

        if Instrument.USE_ACCESS_LOCK:
            if not self._access_lock.acquire():
                logging.warning('Failed to acquire lock!')
                return None

        if fast:
            ret = self._get_value(name, query, **kwargs)
            if Instrument.USE_ACCESS_LOCK:
                self._access_lock.release()
            return ret

        if type(name) in (types.ListType, types.TupleType):
            changed = {}
            result = {}
            for key in name:
                val = self._get_value(key, query, **kwargs)
                if val is not None:
                    result[key] = val
                    changed[key] = val

        else:
            result = self._get_value(name, query, **kwargs)
            changed = {name: result}

        if Instrument.USE_ACCESS_LOCK:
            self._access_lock.release()

        if len(changed) > 0 and query:
            self._queue_changed(changed)

        return result

    def get_all(self):
        '''
        Query all parameters with FLAG_GET flag.
        '''
        keys = []
        for k, v in self._parameters.iteritems():
            if v['flags'] & Instrument.FLAG_GET:
                keys.append(k)
        return self.get(keys)

    def _key_from_format_map_val(self, dic, value):
        for key, val in dic.iteritems():
            if val == value:
                return key
        return None

    def _val_from_option_list(self, opts, value, retidx=False):
        if type(opts[0]) is not type(value):
            return None
        if type(value) is types.StringType:
            value = value.upper()

        match = None
        matches = 0
        for iopt, val in enumerate(opts):
            if type(val) is types.StringType:
                val = val.upper()
                if val.startswith(value):
                    matches += 1
                    if retidx:
                        match = iopt
                    else:
                        match = val.upper()

                # Perfect match
                if val == value:
                    return match

            if val == value:
                if retidx:
                    return iopt
                else:
                    return val

        if matches == 1:
            return match
        else:
            logging.warning('Multiple matches for option %s', value)
            return None

    def _val_from_option_dict(self, opts, value):
        if value in opts:
            return value

        try:
            v = eval(value)
            if v in opts:
                return v
        except:
            pass

        # Not found in the keys, try to match the values
        idx = self._val_from_option_list(opts.values(), value, retidx=True)
        if idx is None:
            return None
        else:
            return opts.keys()[idx]

    _CONVERT_MAP = {
            types.IntType: int,
            types.FloatType: float,
            types.ComplexType: complex,
            types.StringType: str,
            types.BooleanType: bool,
            types.TupleType: tuple,
            types.ListType: list,
            np.ndarray: lambda x: x.tolist(),
    }

    def _convert_value(self, value, ttype):
        if type(value) is types.BooleanType and \
                ttype is not types.BooleanType:
            logging.warning('Setting a boolean, but that is not the expected type')
            raise ValueError()

        if ttype == TYPE_INSTRUMENT:
            if type(value) is types.StringType:
                ins = self.get_instruments()
                if ins is None:
                    return None
                return ins.get(value)
            elif isinstance(value, Instrument) or isinstance(value, objsh.ObjectProxy):
                return value
            else:
                raise ValueError('Unable to convert %s to an Instrument' % value)

        if ttype in (types.ListType, types.TupleType) and type(value) is types.StringType:
            try:
                value = eval(value)
            except:
                logging.warning('Conversion of %r to tuple failed', value)

        if ttype not in self._CONVERT_MAP:
            logging.warning('Unsupported type %s', ttype)
            raise ValueError('Unsupported type %s' % ttype)

        try:
            func = self._CONVERT_MAP[ttype]
            value = func(value)
        except:
            logging.warning('Conversion of %r to type %s failed',
                    value, ttype)
            raise ValueError('Conversion of %r to type %s failed' % (value, ttype))


        return value

    def _set_value(self, name, value, **kwargs):
        '''
        Private wrapper function to set a value.

        Input:  (1) name of parameter (string)
                (2) value of parameter (whatever type the parameter supports).
                    Type casting is performed if necessary.
                (3) Optional keyword args that will be passed on.
        Output: Value returned by the _do_set_<name> function,
                or result of get in FLAG_GET_AFTER_SET specified.
        '''
        if self._parameters.has_key(name):
            p = self._parameters[name]
        else:
            return None

        if not p['flags'] & Instrument.FLAG_SET:
            print 'Instrument does not support setting of %s' % name
            return None

        if 'channel' in p and 'channel' not in kwargs:
            kwargs['channel'] = p['channel']

        # If a format map is available the key should be found.
        if 'format_map' in p:
            newval = self._val_from_option_dict(p['format_map'], value)
            if newval is None:
                logging.error('Value %s is not a valid option for "%s", valid options: %r',
                    value, name, repr(p['format_map']))
                return
            value = newval

        # If an option list is available check whether the value is in there
        if 'option_list' in p:
            newval = self._val_from_option_list(p['option_list'], value)
            if newval is None:
                logging.error('Value %s is not a valid option for "%s", valid: %r',
                    value, name, repr(p['option_list']))
                return
            value = newval

        if 'type' in p:
            try:
                value = self._convert_value(value, p['type'])
            except:
                return None

        if 'minval' in p and value < p['minval']:
            raise Exception('Instrument %s: trying to set too small value for %s: %s' % (self._name, name, value))

        if 'maxval' in p and value > p['maxval']:
            raise Exception('Instrument %s: trying to set too large value for %s: %s' % (self._name, name, value))

        if 'base_name' in p:
            base_name = p['base_name']
        else:
            base_name = name

        func = p['set_func']
        if 'maxstep' in p and p['maxstep'] is not None:
            curval = p['value']
            if curval is None:
                logging.warning('Current value not available, ignoring maxstep')
                curval = value + 0.01 * p['maxstep']

            delta = curval - value
            if delta < 0:
                sign = 1
            else:
                sign = -1

            if 'stepdelay' in p:
                delay = p['stepdelay']
            else:
                delay = 50

            while math.fabs(delta) > 0:
                if math.fabs(delta) > p['maxstep']:
                    curval += sign * p['maxstep']
                    delta += sign * p['maxstep']
                else:
                    curval = value
                    delta = 0

                ret = func(curval, **kwargs)

                if delta != 0:
                    time.sleep(delay / 1000.0)

        else:
            ret = func(value, **kwargs)

        if p['flags'] & self.FLAG_GET_AFTER_SET:
            value = self._get_value(name, **kwargs)

        if p['flags'] & self.FLAG_PERSIST:
            config.set('persist_%s_%s' % (self._name, name), value)
            config.save()

        p['value'] = value
        return value

    def set(self, name, value=None, fast=False, **kwargs):
        '''
        Set one or more Instrument parameter values.

        Checks whether the Instrument is locked and checks value bounds,
        if specified by minval / maxval.

        Input:
            name (string or dict): which parameter to set, or dictionary of
                parameter -> value
            value (any): the value to set
            fast (bool): if True perform as fast as possible, e.g. don't
                emit a signal to update the GUI.
            kwargs: Optional keyword args that will be passed on.

        Output: True or False whether the operation succeeded.
                For multiple sets return False if any of the parameters failed.
        '''

        if self._locked:
            logging.warning('Trying to set value of locked instrument (%s)',
                    self.get_name())
            return False

        if Instrument.USE_ACCESS_LOCK:
            if not self._access_lock.acquire():
                logging.warning('Failed to acquire lock!')
                return None

        result = True
        changed = {}
        if type(name) == types.DictType:

            # If a set order is specified, process those params in the right order
            if self._set_order:
                for k in self._set_order:
                    if k not in name:
                        continue
                    val = self._set_value(k, name.pop(k), **kwargs)
                    if val is not None:
                        changed[k] = val
                    else:
                        result = False

            # Process remaining items
            for key, val in name.iteritems():
                val = self._set_value(key, val, **kwargs)
                if val is not None:
                    changed[key] = val
                else:
                    result = False

        else:
            val = self._set_value(name, value, **kwargs)
            if val is not None:
                changed[name] = val
            else:
                result = False

        if Instrument.USE_ACCESS_LOCK:
            self._access_lock.release()

        if not fast and len(changed) > 0:
            self._queue_changed(changed)

        return result

    def update_value(self, name, value):
        '''
        Update a parameter value if new information is obtained.
        Barely any checking is performed and no type conversions,
        so use with caution.
        '''

        if self._parameters.has_key(name):
            p = self._parameters[name]
        else:
            return None

        p['value'] = value
        self._queue_changed({name: value})

    def get_argspec_dict(self, a):
        return dict(args=a[0], varargs=a[1], keywords=a[2], defaults=a[3])

    def add_function(self, name, **options):
        '''
        Inform the Instrument wrapper class to expose a function.

        Input:  (1) name of function (string)
                (2) dictionary of extra options
        Output: None
        '''

        if not hasattr(self, name):
            logging.warning('Instrument does not implement function %s', name)

        f = getattr(self, name)
        if hasattr(f, '__doc__'):
            options['doc'] = getattr(f, '__doc__')

        options['argspec'] = self.get_argspec_dict(inspect.getargspec(f))

        self._functions[name] = options

    def get_function_options(self, name):
        '''
        Return options for an Instrument function.

        Input:  name of function (string)
        Output: dictionary of options for function 'name'
        '''
        if self._functions.has_key(name):
            return self._functions[name]
        else:
            return None

    def get_function_parameters(self, name):
        '''
        Return info about parameters for function.
        '''
        if self._functions.has_key(name):
            if self._functions[name].has_key('parameters'):
                return self._functions[name]['parameters']
        return None

    def get_function_names(self):
        '''
        Return the list of exposed Instrument function names.

        Input: None
        Output: list of function names (list of strings)
        '''
        return self._functions.keys()

    def get_functions(self):
        '''
        Return the exposed functions dictionary.

        Input: None
        Ouput: Dictionary, keys are function  names, values are the options.
        '''
        return self._functions

    def call(self, funcname, *args, **kwargs):
        '''
        Call the exposed function 'funcname'.

        Input:  (1) function name (string)
                (2) Optional keyword args that will be passed on.
        Output: None
        '''
        f = getattr(self, funcname)
        return f(*args, **kwargs)

    def lock(self):
        '''
        Lock the instrument; no parameters can be changed until the Instrument
        is unlocked.

        Input: None
        Output: None
        '''
        self._locked = True

    def unlock(self):
        '''
        Unlock the instrument; parameters can be changed.

        Input: None
        Output: None
        '''
        self._locked = False

    def set_default_read_var(self, name):
        '''
        For future use.

        Input: name of variable (string)
        Output: None
        '''
        self._default_read_var = name

    def set_default_write_var(self, name):
        '''
        For future use.

        Input: name of variable (string)
        Output: None
        '''
        self._default_write_var = name

    def _get_not_implemented(self, name):
        logging.warning('Get not implemented for %s.%s' % \
            (Instrument.get_type(self), name))

    def _set_not_implemented(self, name):
        logging.warning('Set not implemented for %s.%s' % \
            (Instrument.get_type(self), name))

    def _listen_parameter_changed_cb(self, sender, changed, \
            listen_param, update_func):

        if listen_param not in changed:
            return

        update_func()

    def emit(self, *args, **kwargs):
        pass

    def _do_emit_changed(self):
        if len(self._changed) == 0:
            return False

        self.emit('changed', self._changed)
        self._changed = {}
        self._changed_hid = None
        return False

    def _queue_changed(self, changed):
        self._changed.update(changed)
        if self._changed_hid is None:
            self._changed_hid = timeout_add(1000, self._do_emit_changed)

    @staticmethod
    def test(insclass):
        import pythonprocess
        ap = pythonprocess.ArgParser()
        args, kwargs = ap.parse_args()
        print 'Testing instrument with args %s, keyword args %s' % (args, kwargs)
        ins = insclass(*args, **kwargs)
        for p in ins.get_parameter_names():
            print 'Getting %s' % (p,)
            val = ins.get(p)
            print '  Value %s' % (val,)
        return ins

    # Auxiliary parameter functions

    def _get_aux_info(self, name):
        pi = self._aux_info.get(name, None)
        return pi

    def do_set_aux(self, val, channel=None):
        pi = self._get_aux_info(channel)
        pi['value'] = val
        return pi['ins'].set(pi['param'], val)

    def do_get_aux(self, channel=None):
        pi = self._get_aux_info(channel)
        return pi.get('value', None)

    def add_aux_param(self, insname, param, alias=None):
        '''
        Add a parameter of another instrument to this Qubit.
        This property will not be updated if the instrument changes, as the
        whole idea is to store the relevant settings for this Qubit.
        '''
        if alias is None:
            alias = '%s_%s' % (insname, param)

        srv = self.get_instruments()
        ins = srv.get(insname)
        pinfo = ins.get_shared_parameter_options(param)

        self._aux_info[alias] = dict(
            insname=insname,
            ins=ins,
            param=param,
        )

        # Remove some parameters
        for i in 'flags', 'channel', 'channel_prefix':
            if i in pinfo:
                del pinfo[i]

        self.add_parameter(alias,
                flags=Instrument.FLAG_SET|Instrument.FLAG_GET,
                get_func=self.do_get_aux, set_func=self.do_set_aux,
                channel=alias, **pinfo
        )

    def set_all_aux(self):
        '''
        Set the auxiliary parameter values on the linked instruments.
        '''
        for p, pi in self._aux_info.iteritems():
            pi['ins'].set(pi['param'], pi['value'])

    def get_all_aux(self):
        '''
        Update the auxiliary parameter settings  by getting the parameters
        from the linked instruments.
        '''
        for p, pi in self._aux_info.iteritems():
            v = pi['ins'].get(pi['param'])
            self.set(p, v)

class InvalidInstrument(Instrument):
    '''
    Placeholder class for instruments that fail to load, mainly to support
    reloading.
    '''

    def __init__(self, name, instype, **kwargs):
        self._instype = instype
        self._kwargs = kwargs
        Instrument.__init__(self, name)

    def get_type(self):
        return self._instype

    def get_create_kwargs(self):
        return self._kwargs

