import abc
import pandas as pd
import os


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
        df_dict = {col: [convertible.__dict__[col]] for col in convertible.column_names()}

    writer = pd.ExcelWriter(os.path.join('tmp', filename))
    df = pd.DataFrame(data=df_dict)
    df.to_excel(writer, sheet_name='output')
    writer.save()


def from_excel(filepath):
    with open(filepath, mode='rb') as o:
        excel = pd.read_excel(o, index_col=0)
    return excel
