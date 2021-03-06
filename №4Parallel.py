import pandas as pd
import pandas as pd
import multiprocessing as mp

columnsMap = {
    'ID_REF': 'cpgs',
    'CHR': 'chr',
    'UCSC_REFGENE_NAME': 'gene',
    'RELATION_TO_UCSC_CPG_ISLAND': 'geotype',
    'CROSS_R': 'crossr',
    'Class': 'class',
    'UCSC_REFGENE_GROUP': 'genepart',
}


def inCritFunction(elem, filteredIn):
    for key in filteredIn:
        k, val = key
        if not any(crit in elem[k].split(';') for crit in val):
            return False
    return True


def outCritFunction(elem, filteredOut):
    for key in filteredOut:
        k, val = key
        if any(crit in elem[k].split(';') for crit in val):
            return False
    return True


def combination(elem, filterIn, filterOut):
    return outCritFunction(elem, filterOut) and inCritFunction(elem, filterIn)


def processJobFunction(df, workerNumber, filterIn, filterOut, returnDict):
    # print(df.apply(
    #     combination, axis=1, args=(filterIn, filterOut)))
    z = df[df.apply(
        combination, axis=1, args=(filterIn, filterOut))]
    # returnDict[str(workerNumber), (z['cpgs'].tolist(),
    #                                z.index.values.tolist())]
    # print(z['cpgs'].tolist())
    returnDict[str(workerNumber)] = (z['cpgs'].tolist(),
                                     z.index.values.tolist())


class cpgs_annotation:
    def __init__(self, table, columnNames):
        self.table = table

        self.columns = list(columnsMap.values())
        self.df = pd.DataFrame(data=table, columns=[
            columnsMap[name] if name in columnsMap else name for name in columnNames], dtype=str).filter(self.columns).astype(str)

    def get_cpgs(self, criteries):
        filteredIn = []
        filteredOut = []

        for key, val in criteries.items():
            k = key.split('_')
            if len(k) != 2:
                continue
            if k[0] not in self.columns:
                continue
            if isinstance(val, float):
                continue
            if k[1] == 'in':
                filteredIn.append((k[0], [str(val), ] if isinstance(
                    val, (str, int)) else [str(i) for i in val if not isinstance(val, float)]))
            elif k[1] == 'out':
                filteredOut.append((k[0], [str(val), ] if isinstance(
                    val, (str, int)) else [str(i) for i in val if not isinstance(val, float)]))

        mp.freeze_support()
        manager = mp.Manager()
        return_dict = manager.dict()

        processCount = mp.cpu_count()
        rowCount = len(self.df.index)
        chunk = int(rowCount / processCount)
        chunkArray = [(i*chunk, (i+1) * chunk)
                      for i in range(processCount - 1)]
        chunkArray.append(((processCount - 1) * chunk, rowCount))
        processes = [mp.Process(target=processJobFunction, args=(
            self.df[chunkArray[processNum][0]:chunkArray[processNum][1]], processNum, filteredIn, filteredOut, return_dict)) for processNum in range(processCount)]

        for pr in processes:
            pr.start()

        for pr in processes:
            pr.join()
        z1 = []
        z2 = []
        for i in return_dict:
            z1.extend(return_dict[i][0])
            z2.extend(return_dict[i][1])
        return z1, z2


if __name__ == '__main__':
    # mp.freeze_support()
    # manager = mp.Manager()
    # return_dict = manager.dict()
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

        # {'gene_out': float('nan'), 'chr_in': '7'}
        {'gene_in': 'TMEM49'}
        # {'gene_in': ['TMEM49', 'HAGH', 'POLE3', 'PKD1L3', 'PNPLA6']}
        # {'gene_out': ['TMEM49'], 'gene_in': ['PNPLA6'],
        # 'cpgs_in': ['cg00000029', 'cg00031443']}
        #     # {'gene_out': float('nan'), 'chr_in': '7'}
    )

    print(res)
