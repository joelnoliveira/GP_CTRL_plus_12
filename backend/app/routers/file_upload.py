"""
Router para upload de ficheiros com validação de formatos.
Suporta três tipos:
- scenarios (JSON): Array de objetos com "Id" (int) e "Prompt" (string)
- template_datasets (YAML): Objeto com "prompts" contendo array de {name, data_type, description, parameters, value}
- role_play_options (YAML): Objeto com dataset_name, groups, description, authors, prompts
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel, ValidationError
from typing import List, Optional
from enum import Enum
import json
import yaml
import os
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends
from ..database import get_db
from ..models import Base

router = APIRouter(prefix="/files", tags=["files"])

BASE_DATASETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "datasets",
)

SCENARIOS_DIR = BASE_DATASETS_DIR
TEMPLATE_DATASETS_DIR = BASE_DATASETS_DIR
ROLE_PLAY_DIR = os.path.join(BASE_DATASETS_DIR, "orchestrators", "role_play")

for _dir in [SCENARIOS_DIR, TEMPLATE_DATASETS_DIR, ROLE_PLAY_DIR]:
    os.makedirs(_dir, exist_ok=True)


class FileFormat(str, Enum):
    SCENARIOS = "scenarios"
    TEMPLATE_DATASETS = "template_datasets"
    ROLE_PLAY_OPTIONS = "role_play_options"


# ==================== Schemas JSON ====================


# Schema para validação do formato scenarios
class MaliciousGoalItem(BaseModel):
    Id: int
    Prompt: str


# ==================== Schemas YAML ====================


# Schema para validação do formato template_datasets
class JailbreakPromptItem(BaseModel):
    name: str
    data_type: str
    description: str
    parameters: Optional[List[str]] = None
    value: str


# Schema para validação do formato role_play_options
class RolePlayPromptItem(BaseModel):
    description: Optional[str] = None
    parameters: Optional[List[str]] = None
    value: str


class RolePlayFile(BaseModel):
    dataset_name: str
    groups: Optional[List[str]] = None
    description: Optional[str] = None
    authors: Optional[List[str]] = None
    prompts: List[RolePlayPromptItem]


# ==================== Response Schema ====================


class UploadResponse(BaseModel):
    success: bool
    message: str
    filename: str
    format: str
    items_count: int


# ==================== Validation Functions ====================


def _format_validation_errors(errors: list) -> str:
    parts = []
    for err in errors:
        loc = ".".join(str(p) for p in err.get("loc", []) if p is not None)
        msg = err.get("msg", "Erro de validação")
        if loc:
            parts.append(f"{loc}: {msg}")
        else:
            parts.append(msg)
    return "; ".join(parts) if parts else "Erro de validação no conteúdo"


def _format_json_decode_error(e: json.JSONDecodeError) -> str:
    return (
        f"JSON inválido na linha {e.lineno}, coluna {e.colno}: {e.msg}. "
        "Verifique vírgulas, aspas e chaves." 
    )


def _format_yaml_error(e: yaml.YAMLError) -> str:
    if hasattr(e, "problem_mark") and e.problem_mark is not None:
        mark = e.problem_mark
        return (
            f"YAML inválido na linha {mark.line + 1}, coluna {mark.column + 1}: {getattr(e, 'problem', 'erro de sintaxe')}. "
            "Verifique indentação, hífens e dois-pontos."
        )
    return "YAML inválido: verifique indentação, hífens e dois-pontos."


def validate_malicious_goals_format(data: list) -> tuple[bool, str, int]:
    """Valida se os dados estão no formato scenarios."""
    if not isinstance(data, list):
        return False, "Formato inválido: esperado um array JSON. Exemplo: [{""Id"": 1, ""Prompt"": ""...""}]", 0

    if len(data) == 0:
        return False, "O array não pode estar vazio. Exemplo: [{""Id"": 1, ""Prompt"": ""...""}]", 0

    try:
        for i, item in enumerate(data):
            MaliciousGoalItem(**item)
        return True, "Formato válido", len(data)
    except ValidationError as e:
        details = _format_validation_errors(e.errors())
        return False, f"Erro no item {i}: {details}. Campos obrigatórios: Id (int), Prompt (string).", 0
    except Exception as e:
        return False, f"Erro de validação: {str(e)}", 0


def validate_template_dataset_format(data: dict) -> tuple[bool, str, int]:
    """Valida se os dados estão no formato template_datasets (YAML)."""
    if not isinstance(data, dict):
        return False, "Formato inválido: esperado um objeto YAML com a chave 'prompts'.", 0

    if "prompts" not in data:
        return False, "Falta a chave obrigatória 'prompts'.", 0

    prompts = data.get("prompts", [])
    if not isinstance(prompts, list) or len(prompts) == 0:
        return False, "A chave 'prompts' deve conter um array não vazio.", 0

    try:
        for i, item in enumerate(prompts):
            JailbreakPromptItem(**item)
        return True, "Formato válido", len(prompts)
    except ValidationError as e:
        details = _format_validation_errors(e.errors())
        return (
            False,
            f"Erro no prompt {i}: {details}. Campos obrigatórios: name, data_type, description, value.",
            0,
        )
    except Exception as e:
        return False, f"Erro de validação: {str(e)}", 0


def validate_role_play_format(data: dict) -> tuple[bool, str, int]:
    """Valida se os dados estão no formato role_play_options (YAML)."""
    if not isinstance(data, dict):
        return False, "Formato inválido: esperado um objeto YAML com dataset_name e prompts.", 0

    try:
        role_play = RolePlayFile(**data)
        return True, "Formato válido", len(role_play.prompts)
    except ValidationError as e:
        details = _format_validation_errors(e.errors())
        return False, f"Erro no ficheiro: {details}. Campos obrigatórios: dataset_name e prompts[].", 0
    except Exception as e:
        return False, f"Erro de validação: {str(e)}", 0


def detect_and_validate_json_format(data) -> tuple[bool, str, str, int]:
    """
    Detecta automaticamente o formato do ficheiro JSON e valida.
    Retorna: (sucesso, mensagem, formato_detectado, contagem_items)
    """
    if not isinstance(data, list) or len(data) == 0:
        return False, "JSON inválido: esperado um array não vazio com objetos {Id, Prompt}.", "", 0

    # Tenta detectar pelo primeiro item
    first_item = data[0]

    # Verifica se tem as chaves do formato scenarios (Id, Prompt)
    if "Id" in first_item and "Prompt" in first_item:
        is_valid, msg, count = validate_malicious_goals_format(data)
        return is_valid, msg, FileFormat.SCENARIOS.value, count

    return (
        False,
        "Formato JSON não reconhecido. Esperado: scenarios com objetos {Id, Prompt}.",
        "",
        0,
    )


def detect_and_validate_yaml_format(data) -> tuple[bool, str, str, int]:
    """
    Detecta automaticamente o formato do ficheiro YAML e valida.
    Retorna: (sucesso, mensagem, formato_detectado, contagem_items)
    """
    if not isinstance(data, dict):
        return False, "YAML inválido: esperado um objeto com 'prompts' ou 'dataset_name'.", "", 0

    if "dataset_name" in data:
        is_valid, msg, count = validate_role_play_format(data)
        return is_valid, msg, FileFormat.ROLE_PLAY_OPTIONS.value, count

    if "prompts" in data:
        is_valid, msg, count = validate_template_dataset_format(data)
        return is_valid, msg, FileFormat.TEMPLATE_DATASETS.value, count

    return False, "Formato YAML não reconhecido. Esperado: template_datasets (prompts) ou role_play_options (dataset_name).", "", 0


def _get_target_dir(format_type: str) -> str:
    if format_type == FileFormat.SCENARIOS.value:
        return SCENARIOS_DIR
    if format_type == FileFormat.TEMPLATE_DATASETS.value:
        return TEMPLATE_DATASETS_DIR
    return ROLE_PLAY_DIR


def _get_storage_path(format_type: str, filename: str) -> str:
    if format_type == FileFormat.ROLE_PLAY_OPTIONS.value:
        return f"/backend/datasets/orchestrators/role_play/{filename}"
    return f"/backend/datasets/{filename}"


# ==================== Endpoints ====================


@router.post("/upload/{format_type}", response_model=UploadResponse)
async def upload_file_with_format(
    format_type: FileFormat,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Upload de ficheiro com formato especificado.

    Parâmetros:
    - format_type: 'scenarios', 'template_datasets' ou 'role_play_options'
    """
    filename = file.filename.lower()
    is_json = filename.endswith(".json")
    is_yaml = filename.endswith(".yaml") or filename.endswith(".yml")

    # Validar extensão com base no formato
    if format_type == FileFormat.SCENARIOS and not is_json:
        raise HTTPException(
            status_code=400,
            detail=f"O formato '{format_type.value}' requer um ficheiro .json",
        )

    if format_type in [FileFormat.TEMPLATE_DATASETS, FileFormat.ROLE_PLAY_OPTIONS] and not is_yaml:
        raise HTTPException(
            status_code=400,
            detail=f"O formato '{format_type.value}' requer um ficheiro .yaml ou .yml",
        )

    # Ler conteúdo do ficheiro
    try:
        content = await file.read()
        content_str = content.decode("utf-8")

        if is_json:
            data = json.loads(content_str)
        else:
            data = yaml.safe_load(content_str)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=_format_json_decode_error(e))
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=_format_yaml_error(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler o ficheiro: {str(e)}")

    # Validar formato específico
    if format_type == FileFormat.SCENARIOS:
        is_valid, message, items_count = validate_malicious_goals_format(data)
    elif format_type == FileFormat.TEMPLATE_DATASETS:
        is_valid, message, items_count = validate_template_dataset_format(data)
    else:
        is_valid, message, items_count = validate_role_play_format(data)

    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    # Gerar nome único para o ficheiro
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = name.strip() if name else os.path.splitext(file.filename)[0]
    description_value = description.strip() if description else None
    extension = ".json" if is_json else ".yaml"
    new_filename = f"{base_name}_{timestamp}{extension}"
    file_path = os.path.join(_get_target_dir(format_type.value), new_filename)
    storage_path = _get_storage_path(format_type.value, new_filename)

    # Guardar o ficheiro
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            if is_json:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

        # Atualizar Base de Dados - guardar no destino correto
        try:
            # Garantir que as tabelas estão refletidas
            if not hasattr(Base.classes, 'template_datasets') or not hasattr(Base.classes, 'scenarios') or not hasattr(Base.classes, 'role_play_options'):
                from ..models import reflect_tables
                reflect_tables()

            if format_type == FileFormat.SCENARIOS:
                Scenarios = Base.classes.scenarios
                new_dataset = Scenarios(
                    name=base_name,
                    description=description_value or f"Scenario uploaded: {file.filename}",
                    storage_path=storage_path,
                    is_builtin=False,
                    created_at=datetime.now(),
                )
            elif format_type == FileFormat.TEMPLATE_DATASETS:
                TemplateDatasets = Base.classes.template_datasets
                new_dataset = TemplateDatasets(
                    name=base_name,
                    description=description_value or f"Template dataset uploaded: {file.filename}",
                    storage_path=storage_path,
                    is_builtin=False,
                    created_at=datetime.now(),
                )
            else:
                RolePlayOptions = Base.classes.role_play_options
                new_dataset = RolePlayOptions(
                    name=base_name,
                    description=description_value or f"Role play option uploaded: {file.filename}",
                    storage_path=storage_path,
                    is_builtin=False,
                    created_at=datetime.now(),
                )
            db.add(new_dataset)
            db.commit()
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=500, detail=f"Erro ao guardar na base de dados: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao guardar o ficheiro: {str(e)}"
        )

    return UploadResponse(
        success=True,
        message="Ficheiro validado e guardado com sucesso",
        filename=new_filename,
        format=format_type.value,
        items_count=items_count,
    )


@router.get("/uploads")
async def list_uploaded_files():
    """Lista todos os ficheiros uploaded."""
    try:
        files = []
        for base_dir in [SCENARIOS_DIR, TEMPLATE_DATASETS_DIR, ROLE_PLAY_DIR]:
            if os.path.exists(base_dir):
                for filename in os.listdir(base_dir):
                    if filename.endswith((".json", ".yaml", ".yml")):
                        file_path = os.path.join(base_dir, filename)
                        stat = os.stat(file_path)
                        files.append(
                            {
                                "filename": filename,
                                "size_bytes": stat.st_size,
                                "created_at": datetime.fromtimestamp(
                                    stat.st_ctime
                                ).isoformat(),
                            }
                        )
        return {"files": files, "total": len(files)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar ficheiros: {str(e)}"
        )


@router.delete("/uploads/{filename}")
async def delete_uploaded_file(filename: str, db: Session = Depends(get_db)):
    """Remove um ficheiro uploaded e o registo da base de dados."""
    candidate_paths = [
        os.path.join(SCENARIOS_DIR, filename),
        os.path.join(TEMPLATE_DATASETS_DIR, filename),
        os.path.join(ROLE_PLAY_DIR, filename),
    ]

    file_path = next((p for p in candidate_paths if os.path.exists(p)), None)
    if not file_path:
        raise HTTPException(status_code=404, detail="Ficheiro não encontrado")

    try:
        # Remover da base de dados primeiro
        try:
            if not hasattr(Base.classes, 'template_datasets') or not hasattr(Base.classes, 'scenarios') or not hasattr(Base.classes, 'role_play_options'):
                from ..models import reflect_tables
                reflect_tables()
            
            TemplateDatasets = Base.classes.template_datasets
            Scenarios = Base.classes.scenarios
            RolePlayOptions = Base.classes.role_play_options

            record = db.query(TemplateDatasets).filter(TemplateDatasets.storage_path == _get_storage_path(FileFormat.TEMPLATE_DATASETS.value, filename)).first()
            if record:
                db.delete(record)
                db.commit()
            else:
                record = db.query(Scenarios).filter(Scenarios.storage_path == _get_storage_path(FileFormat.SCENARIOS.value, filename)).first()
                if record:
                    db.delete(record)
                    db.commit()
                else:
                    record = db.query(RolePlayOptions).filter(RolePlayOptions.storage_path == _get_storage_path(FileFormat.ROLE_PLAY_OPTIONS.value, filename)).first()
                    if record:
                        db.delete(record)
                        db.commit()
        except Exception as db_error:
            db.rollback()
            # Log do erro mas continua a apagar o ficheiro
            print(f"Aviso: Erro ao remover da BD: {db_error}")
        
        # Remover o ficheiro físico
        os.remove(file_path)
        return {"success": True, "message": f"Ficheiro '{filename}' removido com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao remover ficheiro: {str(e)}"
        )


@router.get("/formats")
async def list_supported_formats():
    """Lista os formatos suportados para upload."""
    return {
        "formats": [
            {
                "name": FileFormat.SCENARIOS.value,
                "extension": ".json",
                "description": "Array de objetos com 'Id' (int) e 'Prompt' (string)",
                "example": [{"Id": 1, "Prompt": "Example scenario"}],
            },
            {
                "name": FileFormat.TEMPLATE_DATASETS.value,
                "extension": ".yaml",
                "description": "Objeto com 'prompts' contendo array de {name, data_type, description, parameters, value}",
                "example": {
                    "prompts": [
                        {
                            "name": "jailbreakv_28k_0",
                            "data_type": "text",
                            "description": "JailBreakV_28K only unique template prompts",
                            "parameters": ["prompt"],
                            "value": "Example template",
                        }
                    ]
                },
            },
            {
                "name": FileFormat.ROLE_PLAY_OPTIONS.value,
                "extension": ".yaml",
                "description": "Objeto com dataset_name, groups, description, authors, prompts",
                "example": {
                    "dataset_name": "mr_robot",
                    "groups": ["AI Red Team"],
                    "description": "Example role play dataset",
                    "authors": ["João Donato"],
                    "prompts": [
                        {
                            "description": "This used to rephrase the user's objective",
                            "parameters": ["objective"],
                            "value": "Example role play prompt",
                        }
                    ],
                },
            },
        ]
    }
