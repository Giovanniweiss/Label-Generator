from blabel import LabelWriter
from PIL import Image
import segno, os, io, base64
from dotenv import load_dotenv

load_dotenv()

# This creates a company_logo variable that is the image loaded directly in memory.
@lambda _: _()
def company_logo():
    company_logo_path = os.getenv("COMPANY_LOGO_PATH", "")
    # Read the image file into a BytesIO object
    with open(company_logo_path, 'rb') as image_file:
        buffer = io.BytesIO(image_file.read())
    
    # Encode the image in base64
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    img_data = f"data:image/png;base64,{img_base64}"
    
    return img_data

def create_stickers(records: dict,
                    output_path: str, 
                    cliente: str,
                    override_qty: bool=False):
    
    # Extracting the necessary values out of the entry.
    keys = {
        "material"  : "DESCRIÇÃO PRODUTO/MATERIAL ",
        "qntd"      : "QTD REAL",
        "desenho"   : "CÓD. PROD.",
        "of"        : "OF",
        "comp"      : "COMP.",
        "larg"      : "LARG."
    }

    # Ensure the QR codes directory exists.
    path_to_qrcode_folder = "qr_codes"
    os.makedirs(path_to_qrcode_folder, exist_ok=True)

    # Create the label writer instance.
    label_writer = LabelWriter(
        "item_template_2.html",
        default_stylesheets=("style.css",)
    )

    # This procedure generates the labels.
    output = []
    for entry in records:
        value_desenho  = entry[keys["desenho"]]
        value_material = entry[keys["material"]]
        value_quantity = entry[keys["qntd"]]
        value_comp     = entry[keys["comp"]]
        value_larg     = entry[keys["larg"]]
        value_of       = entry[keys["of"]]

        # None of this is strictly necessary, but the end result looks better.
        if value_comp == 0:
            value_comp = "-"
        if value_larg == 0:
            value_larg = "-"
        if value_of == 0:
            value_of = "-"
        if value_quantity % 1 == 0:
            value_quantity = int(value_quantity)

        # Defining a function in this context isn't the best, but it works fine.
        def add_to_output(i):
            if override_qty:
                quantity_to_add_to_sticker = value_quantity
            else:
                quantity_to_add_to_sticker = f"{i} / {value_quantity}"
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
                "company_logo"  : company_logo
            })

        # This creates the QR-code using segno.
        qrcode_info     = str(entry[keys["desenho"]]) + str(entry[keys["of"]])
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
        
        # This is to reduce sticker quantities for small items.
        if override_qty:
            add_to_output(0)
        else:
            for i in range(1, int(entry[keys["qntd"]])+1):
                add_to_output(i)

    # Generate the PDF with the labels
    label_writer.write_labels(output, target=output_path)
    return output_path
