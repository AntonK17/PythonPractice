import pandas as pd
import numpy as np
from pandas.core.arrays import integer
from pandas.core.arrays.sparse import dtype

columnsMap = {
    'ID_REF': 'cpgs',
    'CHR': 'chr',
    'UCSC_REFGENE_NAME': 'gene',
    'RELATION_TO_UCSC_CPG_ISLAND': 'geotype',
    'CROSS_R': 'crossr',
    'Class': 'class',
    'UCSC_REFGENE_GROUP': 'genepart',
}


class cpgs_annotation:
    def __init__(self, table, columnNames):
        self.table = table

        self.df = pd.DataFrame(data=table, columns=[
            columnsMap[name] if name in columnsMap else name for name in columnNames], dtype=str).filter(columnsMap.values()).astype(str)
        # print(self.df['cpgs'].dtype)

    def get_cpgs(self, criteries):
        outOperCrit = []
        inOperCrit = []
        for key, val in criteries.items():
            if len(key.split('_')) != 2:
                continue
            col, operator = key.split('_')
            if col not in columnsMap.values():
                continue
            crit = None
            if isinstance(val, float):
                continue
                # crit = self.df[col].astype(
                # str).str.contains(fr'\b{str(val)}\b', regex=True)
            elif isinstance(val, int):
                # crit = self.df[col].astype(
                #     str).str.contains(fr'\b{str(val)}\b', regex=True)
                # crit = self.df[col].astype(
                #     str).str.contains(f'{str(val)}', regex=False)
                crit = self.df[col].str.split(pat=';').apply(
                    lambda x: bool(set(x) & set([str(val)])))
            elif isinstance(val, str):
                # crit = self.df[col].astype(str).str.contains(
                # fr'\b{str(val)}\b', regex=True)
                crit = self.df[col].str.split(pat=';').apply(
                    lambda x: bool(set(x) & set([val])))
            elif isinstance(val, list):
                # crit = self.df[col].astype(str).str.contains(
                # '|'.join(fr'\b{str(i)}\b' for i in val if str(i) != 'nan'), regex=True)
                crit = self.df[col].str.split(pat=';').apply(
                    lambda x: bool(set(x) & set(
                        [str(i) for i in val if (str(i) != 'nan')]))
                )

            if operator == 'out':
                outOperCrit.append(~crit)
                continue
            elif operator == 'in':
                inOperCrit.append(crit)

        df_result = self.df[
            np.logical_and.reduce(
                [
                    *outOperCrit,
                    *inOperCrit
                ]
            )
        ]

        return df_result['cpgs'].tolist(), df_result.index.values.tolist()


if __name__ == '__main__':
    arr = pd.read_csv(
        'C:/Users/??????????????/Documents/PythonProjects/cpgs_annotations_short (1).tsv', sep='\t').values.tolist()

    annot = cpgs_annotation(arr, [
        'ID_REF',
        'CHR',
        'MAPINFO',
        'Probe_SNPs',
        'Probe_SNPs_10',
        'UCSC_REFGENE_NAME',
        'UCSC_REFGENE_ACCESSION',
        'UCSC_REFGENE_GROUP',
        'UCSC_CPG_ISLANDS_NAME',
        'RELATION_TO_UCSC_CPG_ISLAND',
        'Class',
        'BOP',
        'n.CpG',
        'CROSS_R', ])

    res = annot.get_cpgs(

        #     # {'gene_out': float('nan'), 'chr_in': '7'}
        {'gene_in': 'TMEM49'}
        #     # {'gene_in': ['TMEM49', 'HAGH', 'POLE3', 'PKD1L3', 'PNPLA6']}
        #     # {'gene_out': ['TMEM49'], 'gene_in': ['PNPLA6'],
        #     # 'cpgs_in': ['cg00000029', 'cg00031443']}
        #     # {'gene_out': float('nan'), 'chr_in': '7'}
    )

    print(res)
