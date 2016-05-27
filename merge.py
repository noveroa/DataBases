import pandas as pd
from rdkit.Chem import AllChem
from rdkit.Chem import PandasTools
import numpy as np

apps_file = './apps.hdf5'
grants_file = './grants.hdf5'
apps_store = pd.HDFStore(apps_file)
grants_store = pd.HDFStore(grants_file)

apps_can_smi = apps_store['clean']['CAN_SMILES'].as_matrix()
grants_can_smi = grants_store['clean']['CAN_SMILES'].as_matrix()

grants_keep = np.setdiff1d(grants_can_smi, apps_can_smi)

grants_df = grants_store['clean']
grants_df.drop(grants_df.index[~grants_df['CAN_SMILES'].isin(grants_keep)], inplace=True)
grants_df.reset_index(drop=True, inplace=True)
grants_store['clean'] = grants_df

PandasTools.WriteSDF(grants_df, './grants.sdf', idName='CAN_SMILES', properties=['AVGMP'])
