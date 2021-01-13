import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import h5pyd
import logging
import numpy as np
import sys
import config 
from datetime import datetime
import pandas as pd

#################################
def getEndpoint():
    """
    Helper function - get endpoint we'll send http requests to 
    """ 
    endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))
    return endpoint

#################################
ENDPOINT = getEndpoint()

COMPLEX_TYPES = (np.complex, np.complex64, np.complex128)
FLOAT_TYPES= (np.float, np.float16, np.float32, np.float64)

BASIC_FILEPATH = "hdfgroup.org"


#################################

class H5File(object): 
    def __init__(self, filepath):
        self._filepath = filepath
        self.h5file = None 
        self._filename = None
        try: 
            self.h5file = h5pyd.File(filepath, "a", endpoint=ENDPOINT)
            self._filename = self.h5file.filename
        except Exception as e:
            print('Exception occurs when open h5 files, the exception type:', str(e))
            logging.debug('Exception occurs when open h5 files, the exception type: %s', str(e))
    
    def file(self):
        return self.h5file

    def __getitem__(self, group):
        if self.h5file: 
            if group in self.h5file: 
                return self.h5file[group]
            else: 
                print('Cannot find the group or dataset')
        else: 
            raise FileNotFoundError("Failed to open h5 file")
    
    def __setitem__(self, group, val):
        if self.h5file:
            if group in self.h5file:
                if isinstance(val, np.ndarray):
                    print("Fail to assign data to a group")
                elif isinstance(val, str):
                    if val.startswith("/"):
                        val = val.substring(1)
                    if val in self.h5file[group]:
                        print('Assigned group has existed')
                    else: 
                        self.h5file[group].create_group(val)
                else: 
                    print("Do not support this datatype")
            elif isinstance(val, np.ndarray):
                self.h5file.create_dataset(group, data = val)

            elif isinstance(val, str):
                if val.startswith("/"):
                    self.h5file.create_group(group + val)
                else: 
                    self.h5file.create_group(group + "/"+ val)

            else:
                raise KeyError("Do not support this datatype, assign string to create group or numpy array to create dataset. ")
            self.h5file.flush()
        else: 
            raise FileNotFoundError("Failed to open h5 file")
    
    def close(self):
        if self.h5file:
            self.h5file.close()
            logging.debug('File %s has been closed' % self._filename)

class DataSet(H5File):
    """
    A dataset class, storing numpy.narray type data
    """
    def __init__(self, filepath, name):
        super(DataSet, self).__init__(filepath)
        self._name = name
        self.dsetname = name.split('/')[-1]
        self.attrs = {}

        # dataset
        if self._name in self.h5file:
            if isinstance(self.h5file[self._name], h5pyd.Dataset):
                self._dset = self.h5file[self._name]

                self.dtype = self._dset.dtype
                self.size = self._dset.size
                self.shape = self._dset.shape
                self.ndim = self._dset.ndim
            else:
                print("Referenced item is not a dataset")
                self._dset = None
        else:
            self._dset = None
        
        # dataset attributes 
        if self._dset and self._dset.attrs:
            for key, value in self._dset.attrs.items():
                self.attrs[key] = value
        
    def __getitem__(self, idx):
        """ 
        Directly access to data in dataset
        """
        if isinstance(idx, list):
            idx = tuple(idx)
        return self._dset[idx]

    def __setitem__(self, idx, val):
        if isinstance(idx, list):
            idx = tuple(idx)
        
        if isinstance(val, np.ndarray):
            if val.dtype in COMPLEX_TYPES and self.dtype not in COMPLEX_TYPES:
                raise ValueError('Unable to store complex values in non-complex type')
        
        self._dset[idx] = val
        self.flush()

    def flush(self):
        self.h5file.flush()

    def set_attrs(self, **kwargs):
        """
        Set dataset attributes
        """
        for key, value in kwargs.items():
            self._dset.attrs[key] = value
            self.attrs[key] = value
        
        self.flush()
        logging.debug('Set new dataset attributes')
    
    def get_attrs(self):
        return self.attrs

    def get_data(self):
        return self._dset[()]

    def extend(self, data):
        """
        Extend data 
        """
        if not isinstance(data, np.ndarray):
            data = np.array(data)


        try:
            if not self._dset:
                self._dset = self.h5file.create_dataset(self._name, data = data)
            # dimension of dataset and data match
            elif self._dset.ndim == data.ndim:

                old_shape = self._dset.shape
                add_shape = data.shape

                if data.ndim == 1:
                    new_shape = (old_shape[0]+add_shape[0])

                elif data.ndim == 2:
                    new_shape =  (old_shape[0]+add_shape[0], add_shape[1])
                else:
                    raise ValueError("Dimension of data exceeds 2, extention does not succeed")
                
                if data.dtype == self.dtype:
                    self._dset.resize(new_shape)
                    self._dset[old_shape[0]:new_shape[0]] = data
                else: 
                    raise ValueError("Data type mismatch")
            else:
                raise ValueError("Dimension mismatch") 
        except Exception as error:
            print(error)

    def append(self, data):
        """
        Append single data
        """
        self.extend([data])
    
    def delete(self):
        if self._dset:
            del self._dset
            logging.debug('Dataset object %s is deleted', self._name)
        else:
            raise FileNotFoundError('Dataset %s is not found in h5 file %s', self._name, self._filename)
    
    def close(self):
        self.h5file.close()
        logging.debug('Dataset object %s is closed', self._name)
    
    def update(self, data, **kwargs):
        self.extend(data)
        
        # update attrubutes
        for key, value in kwargs.items():
            self.attrs[key] = value
            self._dset.attrs[key] = value

class DataGroup(H5File):
    def __init__(self, filepath, groupname):
        super(DataGroup, self).__init__(filepath)
        self._groupname = groupname

        # group 
        if self._groupname in self.h5file:
            self._item = self.h5file[self._groupname]
        else:
            self._item = self.h5file.create_group(groupname)
        
    def get(self):
        return self._item

    def keys(self):
        return self._item.keys()
    
    def flush(self):
        self.h5file.flush()
    
    def close(self):
        self.h5file.close()
    
    def delete(self):
        del self._item
    
    def create_group(self, subgroup):
        self._item.create_group(subgroup)
    
    def create_dataset(self, name, arr):
        self._item.create_group(name, data = arr)


class TimeSeries(DataGroup):
    def __init__(self, filepath, groupname):
        super(TimeSeries, self).__init__(filepath, groupname)

    def set_data_df(self, df):
        if isinstance(df, pd.DataFrame):
            self._item.create_dataset('Time', data = np.array(df.index))

            for key in df.keys():
                self._item.create_dataset(key, data = np.array(df[key]))
            
            self.flush()
        else: 
            print('Must to assign data with DataFrame type')
    
    def get_data_df(self):
        if self._item and ('Time' in list(self._item.keys())):
            try:
                time_index = pd.todatetime(self._item['Time'])
                df = pd.DataFrame(index=time_index)

                column_index = list(self._item.keys()).remove('Time')
                for column in column_index: 
                    df[column] = df.self._item[column][()]
            except Exception as e:
                print(e)
                print('Can not get data from h5 file')

            return df
        else: 
            print('Can not find dataset group')

    def concat_column(self, new_df):
        """
        Row alignment
        """
        old_df = self.get_data_df()
        set_c = set(old_df.keys()).intersection(set(new_df.keys()))
        if not set_c:
            result = pd.concat([old_df, new_df], axis =1)
            self.set_data_df(result)
        else: 
            print('New dataframe has same key with the storaged dataframe')


    def append(self, new_df):

        time = np.array(new_df.index)
        time_length = len(time)
        time_append = DataSet(self._filename, self._groupname + '/' + 'Time')
        time_append.append(time)
        time_append.close()

        keys = list(new_df.keys())
        for key in keys:
            data = np.array(new_df[key])
            if len(time) == time_length: 
                temp = DataSet(self._filename, self._groupname + '/' + key)
                temp.append(data)
                temp.close()
            else: 
                raise ValueError('Data size mismatches with time index')

        self.flush()


            
        










    


    