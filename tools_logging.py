import logging, sys

def exception_handler(exc_type, exc_value, exc_traceback):
    """Handler for uncaught exceptions."""
    logging.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

def print_and_log_debug(input):
    logging.debug(input)
    print(input)

def logger_setup(logging_filename):
    logging.basicConfig(
        filename = logging_filename,
        level = logging.DEBUG,
        format = "%(asctime)s :: %(levelno)s :: %(lineno)d :: %(message)s")
    sys.excepthook = exception_handler

def close_log_handlers():
    logger = logging.getLogger()
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)

def print_header(lista_path, destino, pdfs_path, cliente_prov, username, logging_filename):
    print_and_log_debug(f"Arquivo log criado com sucesso: {logging_filename}.")
    print_and_log_debug(f"Processo iniciado por {username}.")
    print_and_log_debug("")
    print_and_log_debug(f"Variáveis de input do usuário:")
    print_and_log_debug(f"Endereço lista de materiais: {lista_path}")
    print_and_log_debug(f"Endereço de destino para os arquivos: {destino}")
    print_and_log_debug(f"Endereço do acervo de PDFs: {pdfs_path}")
    print_and_log_debug(f"Nome do cliente: {cliente_prov}")
    print_and_log_debug("")

def write_data_to_log(file, df):
    with open(file, 'a') as f:
        f.write('\n')
        f.write('#' * 50)
        f.write('\n')
        f.write('CSV DATA')
        f.write('\n')
        f.write('#' * 50)
        f.write('\n')
        tolerated_columns = ['ATIVIDADE','NOME','DATA','ARQUIVO']
        df_columns = list(df.columns.values)
        for i in df_columns:
            if i not in tolerated_columns:
                del df[i]
        df.to_csv(f, index=False, lineterminator='\n')