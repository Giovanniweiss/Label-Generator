import pandas as pd
import os

def process_romaneio(lista_filename, quantity_key):

    def filter_by_department(df: pd.DataFrame, department: str):
        filtered_df = df[df['DEPART.'].str.startswith(department)]
        return filtered_df

    def get_prod_list(df):
        department = "PRODUÇÃO"
        romaneio_prod = filter_by_department(df, department[0])
        return romaneio_prod

    def get_almox_list(df):
        department = "ALMOX."
        romaneio_almox = filter_by_department(df, department[0])
        return romaneio_almox

    # Carregamento do arquivo
    client_df = pd.read_excel(lista_filename)
    def find_first_cliente(df):
        prefix = "CLIENTE: "
        for col in client_df.columns:
            for value in client_df[col]:
                if isinstance(value, str) and value.startswith(prefix):
                    return value[len(prefix):]
        return None

    def clean_cell(value):
        if isinstance(value, str):
            return value.rstrip(' \t')
        return value

    # Find the first cell starting with "CLIENTE:"
    cliente = find_first_cliente(client_df)
    df = pd.read_excel(lista_filename, header=4)
    df = df.map(clean_cell)

    # Limpeza de colunas desnecessárias

    df.drop(columns=["CARREGAMENTO", "Unnamed: 10", "Unnamed: 11"], inplace=True)
    df.drop(df.tail(2).index,inplace=True)
    df.dropna(axis=0, how="all", inplace=True)
    def clean_cod_prod(entry):
        # Remove tabs and replace double spaces with single spaces
        return str(entry).replace('\t', '').replace('  ', '')

    # Apply the cleaning function to the "CÓD. PROD." column
    df['CÓD. PROD.'] = df['CÓD. PROD.'].apply(lambda x: clean_cod_prod(x))
    
    for index, row in df.iterrows():
        qty_type = row["UNIDADE"]
        match qty_type:
            case "PÇ" | "CX" | "RL" | "BD" | "SC" | "PC":
                df.loc[index, quantity_key] = row["QNT."]
            case "MT" | "GL":
                df.loc[index, quantity_key] = row["QNT."]
            case "KG":
                df.loc[index, quantity_key] = row["QNT. PÇS"]
            case _:
                df.loc[index, quantity_key] = max(row["QNT."], row["QNT. PÇS"])

    # Separações
    romaneio_completo = df
    romaneio_prod = get_prod_list(df)
    romaneio_almox = get_almox_list(df)

    return romaneio_almox, romaneio_prod, romaneio_completo, cliente

def save_romaneio(filename: str,
                  path: str,
                  romaneio_almox: pd.DataFrame,
                  romaneio_prod: pd.DataFrame,
                  romaneio_completo: pd.DataFrame):

    save_path = os.path.join(path, filename) + ".xlsx"
    with pd.ExcelWriter(save_path) as writer:
        romaneio_almox.to_excel(writer, sheet_name="rom_almox", index=True)
        romaneio_prod.to_excel(writer, sheet_name="rom_prod", index=True)
        romaneio_completo.to_excel(writer, sheet_name="rom_comp", index=True)

    return 0