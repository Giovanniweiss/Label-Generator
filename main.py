import load_romaneio as lr
import sticker_tools as st
import tools_gui as tg
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

@lambda _: _()
def start_time() -> str:
    date = datetime.now()
    return f'{date.strftime("%Y-%m-%d_%H-%M-%S")}'

def main():
    # Get the info from the gui
    lista_path, destino, images_path = tg.abrir_GUI()

    # Create strings and folder, if necessary.
    lista_filename = str(os.path.basename(lista_path))
    lista_filename_no_extension = str(os.path.splitext(os.path.basename(lista_path))[0])
    folder_name = start_time + "_" + lista_filename_no_extension
    destino = os.path.join(destino, folder_name)

    if not os.path.exists(destino):
        os.makedirs(destino)

    # Load the romaneio
    quantity_key = "QTD REAL"
    romaneio_almox, romaneio_prod, romaneio_completo, cliente = lr.process_romaneio(lista_path, quantity_key)

    # Almox Stickers
    almox_output = os.path.join(destino, "etiquetas_almox.pdf")
    st.create_stickers(romaneio_almox, almox_output, cliente)

    # Prod Stickers
    prod_output = os.path.join(destino, "etiquetas_prod.pdf")
    st.create_stickers(romaneio_prod, prod_output, cliente)

    




main()