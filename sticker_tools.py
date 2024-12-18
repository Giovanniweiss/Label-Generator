from blabel import LabelWriter
import segno, os, io, base64, logging
from dotenv import load_dotenv

load_dotenv()
logging.getLogger('fontTools').setLevel(logging.ERROR)
logging.getLogger('weasyprint').setLevel(logging.ERROR)

# This creates a company_logo variable that is the image loaded directly in memory.
@lambda _: _()
def company_logo():
    company_logo_path = os.getenv("COMPANY_LOGO_PATH", "")
    with open(company_logo_path, 'rb') as image_file:
        buffer = io.BytesIO(image_file.read())
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    img_data = f"data:image/png;base64,{img_base64}"
    
    return img_data

def create_stickers(records: dict,
                    output_path: str, 
                    cliente: str,
                    data_adesivo: str,
                    numero_pedido: str,
                    override_qty: bool=False,
                    label_template: str="item_template_2.html",
                    label_css_temp: str="style.css"):
    
    # Extracting the necessary values out of the entry.
    keys = {
        "material"  : "DESCRIÇÃO PRODUTO/MATERIAL ",
        "qntd"      : "QTD REAL",
        "desenho"   : "CÓD. PROD.",
        "of"        : "OF",
        "comp"      : "COMP.",
        "larg"      : "LARG.",
        "unit"      : "UNIDADE"
    }

    # Ensure the QR codes directory exists.
    path_to_qrcode_folder = "qr_codes"
    os.makedirs(path_to_qrcode_folder, exist_ok=True)

    # Create the label writer instance.
    label_writer = LabelWriter(
        label_template,
        default_stylesheets=(label_css_temp,)
    )
    
    # This procedure generates the labels.
    output = []
    for index, entry in enumerate(records):
        value_desenho  = entry[keys["desenho"]]
        value_material = entry[keys["material"]]
        value_quantity = entry[keys["qntd"]]
        value_comp     = entry[keys["comp"]]
        value_larg     = entry[keys["larg"]]
        value_of       = entry[keys["of"]]
        value_unidade  = entry[keys["unit"]]
        no_of_value    = "-"

        logging.debug(f"Processando item {index}: {value_desenho}")

        # None of this is strictly necessary, but the end result looks better.
        if value_comp == 0:
            value_comp = "-"
        if value_larg == 0:
            value_larg = "-"
        if value_of == 0:
            value_of = no_of_value
        if value_quantity % 1 == 0:
            value_quantity = int(value_quantity)

        # Defining a function in this context isn't the best, but it works fine.
        def add_to_output(i):
            if override_qty:
                quantity_to_add_to_sticker = str(value_quantity) + " " + value_unidade
            else:
                quantity_to_add_to_sticker = str(value_quantity) + " "

            output.append({
                "desenho"       : value_desenho,
                "conjunto"      : "",
                "material"      : value_material,
                "qntd"          : quantity_to_add_to_sticker,
                "comp"          : value_comp,
                "larg"          : value_larg,
                "cliente"       : cliente,
                "of"            : value_of,
                "qr_code"       : img_data,
                "data"          : data_adesivo,
                "pedido"        : numero_pedido,
                "company_logo"  : company_logo
            })

        # This creates the QR-code using segno.
        if value_of == no_of_value:
            qrcode_info = str(entry[keys["desenho"]])
        else:
            qrcode_info = str(entry[keys["desenho"]]) + " " + str(entry[keys["of"]])
        qrcode_filename = qrcode_info + ".png"
        qrcode = segno.make_qr(qrcode_info, version=3)

        # Funky method, but this works as opposed to linking the file.
        buffer = io.BytesIO()
        qrcode.save(buffer, kind='png', scale=3)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        img_data = f"data:image/png;base64,{img_base64}"

        # Keep a backup of the QR-codes.
        qrcode_savepath = os.path.join(path_to_qrcode_folder, qrcode_filename)
        qrcode.save(qrcode_savepath, kind='png', scale=3)
        logging.debug(f"Gerado QR Code do item {value_desenho} em {qrcode_savepath}")
        
        # This is to reduce sticker quantities for small items.
        # if override_qty:
        #     add_to_output(0)
        # else:
        #     for i in range(1, int(entry[keys["qntd"]])+1):
        #         add_to_output(i)

        add_to_output(0)

    # Generate the PDF with the labels
    label_writer.write_labels(output, target=output_path)
    return output_path
