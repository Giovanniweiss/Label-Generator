from blabel import LabelWriter
from PIL import Image
import segno, os, io, base64
from dotenv import load_dotenv

load_dotenv()

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

def create_stickers(records, output_path, cliente):
    output = []
    keys = {
        "material"  : "DESCRIÇÃO PRODUTO/MATERIAL ",
        "qntd"      : "QTD REAL",
        "desenho"   : "CÓD. PROD.",
        "of"        : "OF",
        "comp"      : "COMP.",
        "larg"      : "LARG."
    }

    # Ensure the QR codes directory exists
    path_to_qrcode_folder = "qr_codes"
    os.makedirs(path_to_qrcode_folder, exist_ok=True)


    label_writer = LabelWriter(
        "item_template_2.html",
        default_stylesheets=("style.css",)
    )

    for entry in records:
        qrcode_filename = str(entry[keys["desenho"]]) + str(entry[keys["of"]]) + ".png"
        qrcode = segno.make_qr(qrcode_filename, error="H")

        # Save QR code to an in-memory file
        buffer = io.BytesIO()
        qrcode.save(buffer, kind='png', scale=3)
        buffer.seek(0)
        
        # Encode the QR code in base64
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        img_data = f"data:image/png;base64,{img_base64}"

        qrcode_savepath = os.path.join(path_to_qrcode_folder, qrcode_filename)
        qrcode.save(qrcode_savepath, kind='png', scale=3)
        

        for i in range(int(entry[keys["qntd"]])):
            output.append({
                "desenho"       : entry[keys["desenho"]],
                "conjunto"      : "",
                "material"      : entry[keys["material"]],
                "qntd"          : f"i / {entry[keys["qntd"]]}",
                "comp"          : entry[keys["comp"]],
                "larg"          : entry[keys["larg"]],
                "cliente"       : cliente,
                "of"            : entry[keys["of"]],
                "qr_code"       : img_data,  # Directly use base64 encoded image
                "company_logo"  : company_logo
            })

    # Generate the PDF with the labels
    label_writer.write_labels(output, target=output_path)
