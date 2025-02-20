from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.services.csv_importer_service import CSVImporterService
from app.schemas.csv_importer import CSVImportResponse


class CSVImporterHandler:
    """Handler responsável pelo processamento do upload de arquivos CSV."""

    @staticmethod
    def upload_csv(db: Session, file: UploadFile) -> CSVImportResponse:
        """
        Processa o upload de um arquivo CSV e salva os dados no banco de dados.

        :param db: Sessão do banco de dados.
        :param file: Arquivo CSV enviado pelo usuário.
        :return: Mensagem de sucesso ou erro.
        """
        if not file.filename or not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="O arquivo deve ser um CSV.")

        try:
            csv_content = file.file.read().decode("utf-8")
            return CSVImporterService.import_csv(db, csv_content)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao processar o CSV: {str(e)}"
            )
