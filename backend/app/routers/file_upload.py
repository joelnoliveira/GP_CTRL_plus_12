"""
Router para upload de ficheiros com validação de formatos.
Suporta quatro formatos:
- malicious_goals (JSON): Array de objetos com "Id" (int) e "Prompt" (string)
- vulnerable_goals (JSON): Array de objetos com "ID" (string), "CWE" (string) e "Prompt" (string)
- or_bench (YAML): Objeto com "prompts" contendo array de {data_type, description, name, value}
- jailbreak (YAML): Objeto com "prompts" contendo array de {name, data_type, description, parameters, value}
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
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

# Diretório onde os ficheiros serão guardados
UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "datasets",
    "uploads",
)

# Criar o diretório se não existir
os.makedirs(UPLOAD_DIR, exist_ok=True)


class FileFormat(str, Enum):
    MALICIOUS_GOALS = "malicious_goals"
    VULNERABLE_GOALS = "vulnerable_goals"
    OR_BENCH = "or_bench"
    JAILBREAK = "jailbreak"


# ==================== Schemas JSON ====================


# Schema para validação do formato malicious_goals
class MaliciousGoalItem(BaseModel):
    Id: int
    Prompt: str


# Schema para validação do formato vulnerable_goals
class VulnerableGoalItem(BaseModel):
    ID: str
    CWE: str
    Prompt: str


# ==================== Schemas YAML ====================


# Schema para validação do formato or_bench (or-bench-hard-1k.yaml)
class OrBenchPromptItem(BaseModel):
    data_type: str
    description: str
    name: str
    value: str


class OrBenchFile(BaseModel):
    prompts: List[OrBenchPromptItem]


# Schema para validação do formato jailbreak (JailBreakV_28K_clean.yaml)
class JailbreakPromptItem(BaseModel):
    name: str
    data_type: str
    description: str
    parameters: Optional[List[str]] = None
    value: str


class JailbreakFile(BaseModel):
    prompts: List[JailbreakPromptItem]


# ==================== Response Schema ====================


class UploadResponse(BaseModel):
    success: bool
    message: str
    filename: str
    format: str
    items_count: int


# ==================== Validation Functions ====================


def validate_malicious_goals_format(data: list) -> tuple[bool, str, int]:
    """Valida se os dados estão no formato malicious_goals."""
    if not isinstance(data, list):
        return False, "O ficheiro deve conter um array JSON", 0

    if len(data) == 0:
        return False, "O array não pode estar vazio", 0

    try:
        for i, item in enumerate(data):
            MaliciousGoalItem(**item)
        return True, "Formato válido", len(data)
    except ValidationError as e:
        return False, f"Erro de validação no item {i}: {str(e)}", 0
    except Exception as e:
        return False, f"Erro de validação: {str(e)}", 0


def validate_vulnerable_goals_format(data: list) -> tuple[bool, str, int]:
    """Valida se os dados estão no formato vulnerable_goals."""
    if not isinstance(data, list):
        return False, "O ficheiro deve conter um array JSON", 0

    if len(data) == 0:
        return False, "O array não pode estar vazio", 0

    try:
        for i, item in enumerate(data):
            VulnerableGoalItem(**item)
        return True, "Formato válido", len(data)
    except ValidationError as e:
        return False, f"Erro de validação no item {i}: {str(e)}", 0
    except Exception as e:
        return False, f"Erro de validação: {str(e)}", 0


def validate_or_bench_format(data: dict) -> tuple[bool, str, int]:
    """Valida se os dados estão no formato or_bench (YAML)."""
    if not isinstance(data, dict):
        return False, "O ficheiro YAML deve conter um objeto com 'prompts'", 0

    if "prompts" not in data:
        return False, "O ficheiro deve conter a chave 'prompts'", 0

    prompts = data.get("prompts", [])
    if not isinstance(prompts, list) or len(prompts) == 0:
        return False, "A chave 'prompts' deve conter um array não vazio", 0

    try:
        for i, item in enumerate(prompts):
            OrBenchPromptItem(**item)
        return True, "Formato válido", len(prompts)
    except ValidationError as e:
        return False, f"Erro de validação no prompt {i}: {str(e)}", 0
    except Exception as e:
        return False, f"Erro de validação: {str(e)}", 0


def validate_jailbreak_format(data: dict) -> tuple[bool, str, int]:
    """Valida se os dados estão no formato jailbreak (YAML)."""
    if not isinstance(data, dict):
        return False, "O ficheiro YAML deve conter um objeto com 'prompts'", 0

    if "prompts" not in data:
        return False, "O ficheiro deve conter a chave 'prompts'", 0

    prompts = data.get("prompts", [])
    if not isinstance(prompts, list) or len(prompts) == 0:
        return False, "A chave 'prompts' deve conter um array não vazio", 0

    try:
        for i, item in enumerate(prompts):
            JailbreakPromptItem(**item)
        return True, "Formato válido", len(prompts)
    except ValidationError as e:
        return False, f"Erro de validação no prompt {i}: {str(e)}", 0
    except Exception as e:
        return False, f"Erro de validação: {str(e)}", 0


def detect_and_validate_json_format(data) -> tuple[bool, str, str, int]:
    """
    Detecta automaticamente o formato do ficheiro JSON e valida.
    Retorna: (sucesso, mensagem, formato_detectado, contagem_items)
    """
    if not isinstance(data, list) or len(data) == 0:
        return False, "O ficheiro JSON deve conter um array não vazio", "", 0

    # Tenta detectar pelo primeiro item
    first_item = data[0]

    # Verifica se tem as chaves do formato malicious_goals (Id, Prompt)
    if "Id" in first_item and "Prompt" in first_item:
        is_valid, msg, count = validate_malicious_goals_format(data)
        return is_valid, msg, FileFormat.MALICIOUS_GOALS.value, count

    # Verifica se tem as chaves do formato vulnerable_goals (ID, CWE, Prompt)
    if "ID" in first_item and "CWE" in first_item and "Prompt" in first_item:
        is_valid, msg, count = validate_vulnerable_goals_format(data)
        return is_valid, msg, FileFormat.VULNERABLE_GOALS.value, count

    return (
        False,
        "Formato JSON não reconhecido. Esperado: malicious_goals (Id, Prompt) ou vulnerable_goals (ID, CWE, Prompt)",
        "",
        0,
    )


def detect_and_validate_yaml_format(data) -> tuple[bool, str, str, int]:
    """
    Detecta automaticamente o formato do ficheiro YAML e valida.
    Retorna: (sucesso, mensagem, formato_detectado, contagem_items)
    """
    if not isinstance(data, dict) or "prompts" not in data:
        return False, "O ficheiro YAML deve conter um objeto com 'prompts'", "", 0

    prompts = data.get("prompts", [])
    if not isinstance(prompts, list) or len(prompts) == 0:
        return False, "A chave 'prompts' deve conter um array não vazio", "", 0

    # Tenta detectar pelo primeiro item
    first_item = prompts[0]

    # Verifica se tem 'parameters' - característico do formato jailbreak
    if "parameters" in first_item:
        is_valid, msg, count = validate_jailbreak_format(data)
        return is_valid, msg, FileFormat.JAILBREAK.value, count

    # Senão, assume formato or_bench
    if "data_type" in first_item and "name" in first_item and "value" in first_item:
        is_valid, msg, count = validate_or_bench_format(data)
        return is_valid, msg, FileFormat.OR_BENCH.value, count

    return (
        False,
        "Formato YAML não reconhecido. Esperado: or_bench ou jailbreak",
        "",
        0,
    )


# ==================== Helper Functions ====================


def _get_scenario_for_format(format_type: str) -> str:
    """Retorna o nome do scenario baseado no formato do ficheiro."""
    mapping = {
        FileFormat.MALICIOUS_GOALS.value: "Single Turn Attack",
        FileFormat.VULNERABLE_GOALS.value: "Single Turn Attack",
        FileFormat.OR_BENCH.value: "Over-Refusal Test",
        FileFormat.JAILBREAK.value: "Template Attack",
    }
    return mapping.get(format_type, "Single Turn Attack")


# ==================== Endpoints ====================


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload de ficheiro com detecção automática de formato.

    Formatos suportados:
    - JSON:
        - malicious_goals: Array de {"Id": int, "Prompt": string}
        - vulnerable_goals: Array de {"ID": string, "CWE": string, "Prompt": string}
    - YAML:
        - or_bench: {prompts: [{data_type, description, name, value}]}
        - jailbreak: {prompts: [{name, data_type, description, parameters, value}]}
    """
    filename = file.filename.lower()
    is_json = filename.endswith(".json")
    is_yaml = filename.endswith(".yaml") or filename.endswith(".yml")

    if not is_json and not is_yaml:
        raise HTTPException(
            status_code=400, detail="Apenas ficheiros .json, .yaml ou .yml são aceites"
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
        raise HTTPException(status_code=400, detail=f"Ficheiro JSON inválido: {str(e)}")
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Ficheiro YAML inválido: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler o ficheiro: {str(e)}")

    # Validar formato
    if is_json:
        is_valid, message, detected_format, items_count = detect_and_validate_json_format(data)
    else:
        is_valid, message, detected_format, items_count = detect_and_validate_yaml_format(data)

    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    # Gerar nome único para o ficheiro
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(file.filename)[0]
    extension = ".json" if is_json else ".yaml"
    new_filename = f"{base_name}_{timestamp}{extension}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    # Guardar o ficheiro
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            if is_json:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

        # Atualizar Base de Dados - guardar em workload_datasets
        try:
            # Garantir que as tabelas estão refletidas
            if not hasattr(Base.classes, 'workload_datasets'):
                from ..models import reflect_tables
                reflect_tables()
            
            WorkloadDatasets = Base.classes.workload_datasets
            Scenarios = Base.classes.scenarios
            
            # Determinar o scenario_id baseado no formato
            scenario_name = _get_scenario_for_format(detected_format)
            scenario = db.query(Scenarios).filter(Scenarios.name == scenario_name).first()
            
            if not scenario:
                raise HTTPException(status_code=500, detail=f"Scenario '{scenario_name}' não encontrado na BD")
            
            # Criar o novo dataset
            new_dataset = WorkloadDatasets(
                name=base_name,
                description=f"Dataset uploaded: {file.filename}",
                storage_path=file_path,
                mime_path="application/json" if is_json else "application/x-yaml",
                is_builtin=False,
                created_at=datetime.now(),
                scenarios_id=scenario.id
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
        format=detected_format,
        items_count=items_count,
    )


@router.post("/upload/{format_type}", response_model=UploadResponse)
async def upload_file_with_format(format_type: FileFormat, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload de ficheiro com formato especificado.

    Parâmetros:
    - format_type: 'malicious_goals', 'vulnerable_goals', 'or_bench' ou 'jailbreak'
    """
    filename = file.filename.lower()
    is_json = filename.endswith(".json")
    is_yaml = filename.endswith(".yaml") or filename.endswith(".yml")

    # Validar extensão com base no formato
    json_formats = [FileFormat.MALICIOUS_GOALS, FileFormat.VULNERABLE_GOALS]
    yaml_formats = [FileFormat.OR_BENCH, FileFormat.JAILBREAK]

    if format_type in json_formats and not is_json:
        raise HTTPException(
            status_code=400,
            detail=f"O formato '{format_type.value}' requer um ficheiro .json",
        )

    if format_type in yaml_formats and not is_yaml:
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
        raise HTTPException(status_code=400, detail=f"Ficheiro JSON inválido: {str(e)}")
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Ficheiro YAML inválido: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler o ficheiro: {str(e)}")

    # Validar formato específico
    if format_type == FileFormat.MALICIOUS_GOALS:
        is_valid, message, items_count = validate_malicious_goals_format(data)
    elif format_type == FileFormat.VULNERABLE_GOALS:
        is_valid, message, items_count = validate_vulnerable_goals_format(data)
    elif format_type == FileFormat.OR_BENCH:
        is_valid, message, items_count = validate_or_bench_format(data)
    else:  # JAILBREAK
        is_valid, message, items_count = validate_jailbreak_format(data)

    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    # Gerar nome único para o ficheiro
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(file.filename)[0]
    extension = ".json" if is_json else ".yaml"
    new_filename = f"{base_name}_{timestamp}{extension}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    # Guardar o ficheiro
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            if is_json:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

        # Atualizar Base de Dados - guardar em workload_datasets
        try:
            # Garantir que as tabelas estão refletidas
            if not hasattr(Base.classes, 'workload_datasets'):
                from ..models import reflect_tables
                reflect_tables()

            WorkloadDatasets = Base.classes.workload_datasets
            Scenarios = Base.classes.scenarios
            
            # Determinar o scenario_id baseado no formato
            scenario_name = _get_scenario_for_format(format_type.value)
            scenario = db.query(Scenarios).filter(Scenarios.name == scenario_name).first()
            
            if not scenario:
                raise HTTPException(status_code=500, detail=f"Scenario '{scenario_name}' não encontrado na BD")
            
            # Criar o novo dataset
            new_dataset = WorkloadDatasets(
                name=base_name,
                description=f"Dataset uploaded: {file.filename}",
                storage_path=file_path,
                mime_path="application/json" if is_json else "application/x-yaml",
                is_builtin=False,
                created_at=datetime.now(),
                scenarios_id=scenario.id
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
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                if filename.endswith((".json", ".yaml", ".yml")):
                    file_path = os.path.join(UPLOAD_DIR, filename)
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
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Ficheiro não encontrado")

    try:
        # Remover da base de dados primeiro
        try:
            if not hasattr(Base.classes, 'workload_datasets'):
                from ..models import reflect_tables
                reflect_tables()
            
            WorkloadDatasets = Base.classes.workload_datasets
            # Procurar pelo storage_path (pode ter path completo ou só o nome)
            record = db.query(WorkloadDatasets).filter(
                WorkloadDatasets.storage_path == file_path
            ).first()
            
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
                "name": FileFormat.MALICIOUS_GOALS.value,
                "extension": ".json",
                "description": "Array de objetos com 'Id' (int) e 'Prompt' (string)",
                "example": [{"Id": 1, "Prompt": "Example malicious goal"}],
            },
            {
                "name": FileFormat.VULNERABLE_GOALS.value,
                "extension": ".json",
                "description": "Array de objetos com 'ID' (string), 'CWE' (string) e 'Prompt' (string)",
                "example": [
                    {"ID": "CWE-20_IIV-1b", "CWE": "Improper Input Validation", "Prompt": "Example"}
                ],
            },
            {
                "name": FileFormat.OR_BENCH.value,
                "extension": ".yaml",
                "description": "Objeto com 'prompts' contendo array de {data_type, description, name, value}",
                "example": {
                    "prompts": [
                        {
                            "data_type": "text",
                            "description": "OR-bench prompt",
                            "name": "or-bench-0",
                            "value": "Example prompt",
                        }
                    ]
                },
            },
            {
                "name": FileFormat.JAILBREAK.value,
                "extension": ".yaml",
                "description": "Objeto com 'prompts' contendo array de {name, data_type, description, parameters, value}",
                "example": {
                    "prompts": [
                        {
                            "name": "jailbreak_0",
                            "data_type": "text",
                            "description": "Jailbreak prompt",
                            "parameters": ["prompt"],
                            "value": "Example jailbreak template",
                        }
                    ]
                },
            },
        ]
    }
