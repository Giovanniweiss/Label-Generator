# Import libraries
import os, pandas as pd, getpass, logging, shutil
from dotenv import load_dotenv
from datetime import datetime

# Import tool modules for this code
import load_romaneio as lr
import sticker_tools as st
import tools_gui as tg
import tools_logging as tl

load_dotenv()

@lambda _: _()
def start_time() -> str:
    date = datetime.now()
    return f'{date.strftime("%Y-%m-%d_%H-%M-%S")}'


def get_data_from_gui():
    lista_path, target_folder = tg.abrir_GUI()
    return lista_path, target_folder


def main(lista_path: str,
         target_folder: str):

    # Get the info from the gui
    username = str(getpass.getuser())

    # Create strings and folder, if necessary.
    lista_filename = str(os.path.basename(lista_path))
    lista_filename_no_extension = str(os.path.splitext(os.path.basename(lista_path))[0])
    folder_name = start_time + "_" + lista_filename_no_extension
    destino = os.path.join(target_folder, folder_name)

    # Loggin setup.
    log_foldername = "./logs/" # This is bad, but works for now.
    logging_filename = folder_name + ".log"
    tl.logger_setup(logging_filename)
    tl.print_header(lista_path, target_folder, username, logging_filename)

    # Create the target folder if it does not exist.
    if not os.path.exists(destino):
        os.makedirs(destino)
        tl.print_and_log_debug(f"Pasta '{destino}' criada com sucesso em '{target_folder}'.")
    else:
        tl.print_and_log_debug(f"Pasta '{destino}' já existe em '{target_folder}'.")

    # Load the romaneio
    quantity_key = "QTD REAL"
    tl.print_and_log_debug(f"Iniciando processamento do romenaio. Chave para quantidade considerada: {quantity_key}")
    romaneio_almox, romaneio_prod, romaneio_completo, cliente = lr.process_romaneio(lista_path, quantity_key)
    romaneio_filename = "_".join(["relatorio", start_time])
    lr.save_romaneio(romaneio_filename, destino, romaneio_almox, romaneio_prod, romaneio_completo)
    tl.print_and_log_debug(f"Romaneio processado com sucesso. Cópia salva em {destino} sob o nome {romaneio_filename}")

    romaneio_completo = romaneio_completo.to_dict(orient='records')
    romaneio_prod = romaneio_prod.to_dict(orient='records')
    romaneio_almox = romaneio_almox.to_dict(orient='records')

    if len(cliente) > 20:
        cliente = cliente[:20]
        tl.print_and_log_debug(f"Nome do cliente identificado muito comprido. Truncado para {cliente}.")

    # Almox Stickers
    tl.print_and_log_debug("Iniciando geração dos adesivos do departamento ALMOX.")
    try:
        almox_output = os.path.join(destino, "_".join([cliente, "etiq_almox"]) + ".pdf")
        output_path_1 = st.create_stickers(romaneio_almox, almox_output, cliente, override_qty=True)
        tl.print_and_log_debug(f"Processados adesivos do ALMOX. Salvo PDF em: {output_path_1}")
    except Exception as e:
        tl.print_and_log_debug(f"Falha ao processar os adesivos para ALMOX. Erro apontado: {e}")
        raise e
    
    # Prod Stickers
    tl.print_and_log_debug("Iniciando geração dos adesivos do departamento PRODUÇÃO.")
    try:
        prod_output = os.path.join(destino, "_".join([cliente, "etiq_prod"]) + ".pdf")
        output_path_2 = st.create_stickers(romaneio_prod, prod_output, cliente, override_qty=False)
        tl.print_and_log_debug(f"Processados adesivos da PRODUÇÃO. Salvo PDF em: {output_path_2}")
    except Exception as e:
        tl.print_and_log_debug(f"Falha ao processar os adesivos para PRODUÇÃO. Erro apontado: {e}")
        raise e


    final = input("Finalizada geração de adesivos. Pressione enter para finalizar o programa.")
    logging.debug(f"{final}")
    tl.close_log_handlers()

    # Move the logs file
    if not os.path.exists(log_foldername):
        os.makedirs(log_foldername)
    shutil.move(logging_filename, log_foldername)

if __name__ == "__main__":
    lista_path, target_folder = get_data_from_gui()
    main(lista_path, target_folder)