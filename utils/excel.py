import abc
import pandas as pd
import os


class ExcelConvertible(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def column_names(self):
        pass


def to_excel(convertible, filename):
    """
    엑셀로 변환할 수 있는 객체들을 엑셀 파일로 저장합니다. 저장 경로는 {working directory}/tmp/{filename}입니다.
    :param convertible: ExcelConvertible을 구현한 클래스의 객체 또는 그 리스트
    :type convertible: Union[ExcelConvertible, Iterable[ExcelConvertible]]
    :param filename: 저장할 파일의 이름.
    :type filename: str
    """
    df_dict = {}
    try:
        for x in iter(convertible):
            for col in x.column_names():
                if col in df_dict:
                    df_dict[col].append(x.__dict__[col])
                else:
                    df_dict[col] = [x.__dict__[col]]
    except TypeError:
        df_dict = {col: [convertible.__dict__[col]] for col in convertible.column_names()}

    writer = pd.ExcelWriter(os.path.join('tmp', filename))
    df = pd.DataFrame(data=df_dict)
    df.to_excel(writer, sheet_name='output')
    writer.save()


def from_excel(file_path):
    with open(file_path, mode='rb') as o:
        excel = pd.read_excel(o, index_col=0)
    return excel
