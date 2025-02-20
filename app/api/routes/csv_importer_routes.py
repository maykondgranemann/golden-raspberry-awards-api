from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.handlers.csv_importer_handler import CSVImporterHandler
from app.schemas.csv_importer import CSVImportResponse

router = APIRouter(prefix="/csv", tags=["CSV Importer"])


@router.post("/upload", response_model=CSVImportResponse)
def upload_csv(
    file: UploadFile = File(...), db: Session = Depends(get_db)
) -> CSVImportResponse:
    """
    Endpoint para upload de um arquivo CSV e importação dos dados.

    :param file: Arquivo CSV enviado pelo usuário.
    :param db: Sessão do banco de dados.
    :return: Mensagem de sucesso e quantidade de filmes importados.
    """
    return CSVImporterHandler.upload_csv(db, file)
