import pandas as pd
import os

def process_romaneio(lista_filename, quantity_key):

    def filter_by_department(df: pd.DataFrame, department: str):
        filtered_df = df[df['DEPTO.'].str.startswith(department)]
        return filtered_df

    def get_prod_list(df):
        department = "PROD."
        romaneio_prod = filter_by_department(df, department[0])
        return romaneio_prod

    def get_almox_list(df):
        department = "ALMX."
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
        return "Cliente Indeterminado"

    def find_cliente(df):
        print(df)
        cliente_tag = 'CLIENTE: '
        try:
        #    for idx, row in df.iterrows():
        #        if cliente_tag in row.values:
        #            cliente_col = str(row[str(row).startswith(cliente_tag)].index[0])
        #            cliente_col_idx = df.columns.get_loc(cliente_col)  
        #            return cliente_col.split(cliente_tag)[0]
            return str(df.iat[0,3]).split(cliente_tag)[1]
        except:
            return "Cliente Indeterminado"

    def clean_cell(value):
        if isinstance(value, str):
            return value.rstrip(' \t')
        return value

    # Find the first cell starting with "CLIENTE:"
    #cliente = find_first_cliente(client_df)
    cliente = find_cliente(client_df)

    # Achar o numero do pedido
    numero_pedido = client_df.iat[0,11]

    df = pd.read_excel(lista_filename, header=4)
    df = df.map(clean_cell)

    # Limpeza de colunas desnecessárias

    imagem_index = df.columns.get_loc("IMAGEM")
    df = df.iloc[:, :imagem_index]
    df.drop(df.tail(2).index,inplace=True)
    df.dropna(axis=0, how="all", inplace=True)
    df = df.fillna(0)
    def clean_cod_prod(entry):
        # Remove tabs and replace double spaces with single spaces
        return str(entry).replace('\t', '').replace('  ', '')

    # Apply the cleaning function to the "CÓD. PROD." column
    df['CÓD. PROD.'] = df['CÓD. PROD.'].apply(lambda x: clean_cod_prod(x))
    
    for index, row in df.iterrows():
        # This sucks because the methodology sucks, can't do better than this crap
        qty_type = row["UN."]
        match qty_type:
            case "PÇ" | "CX" | "RL" | "BD" | "SC" | "PC":
                df.loc[index, quantity_key] = row["QNT."]
            case "MT" | "GL":
                df.loc[index, quantity_key] = row["QNT."]
            case "KG":
                df.loc[index, quantity_key] = row["PÇS"]
            case _:
                df.loc[index, quantity_key] = max(row["QNT."], row["QNT. PÇS"])

    # Separações
    romaneio_completo = df
    romaneio_prod = get_prod_list(df)
    romaneio_almox = get_almox_list(df)

    return romaneio_almox, romaneio_prod, romaneio_completo, cliente, numero_pedido

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
