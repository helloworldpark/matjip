import abc
import pandas as pd
from typing import Union
import os
import traceback


class ExcelConvertible(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def column_names(self):
        pass

    def row(self):
        return (self.__dict__[x] for x in self.column_names())


def to_excel(convertible, filename):
    """

    :param convertible:
    :type convertible: Union[ExcelConvertible, Iterable[ExcelConvertible]]
    :param filename:
    :type filename: str
    :return:
    """
    df_dict = {}
    try:
        for x in iter(convertible):
            for col in x.column_names():
                if col in df_dict:
                    df_dict[col].append(x.__dict__[col])
                else:
                    df_dict[col] = [x.__dict__[col]]
    except StopIteration:
        pass
    except TypeError:
        for col in convertible.column_names():
            if col in df_dict:
                df_dict[col].append(convertible.__dict__[col])
            else:
                df_dict[col] = [convertible.__dict__[col]]

    writer = pd.ExcelWriter(os.path.join('tmp', filename))
    df = pd.DataFrame(data=df_dict)
    df.to_excel(writer, sheet_name='output')
    writer.save()


