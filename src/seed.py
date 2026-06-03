"""Initial seed data for econometric models and their variables."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.models.entities import EconModel, ModelVariable, Variable

MODELS_DATA = [
    {
        "name": "econ_growth",
        "display_name": "Determinantes del Crecimiento Económico de Pereira",
        "description": (
            "Estima la variación esperada del PIB de Pereira a partir del comportamiento "
            "de sus principales canales de actividad económica: comercio exterior, remesas, "
            "inversión neta y tejido empresarial. El resultado del modelo es Δln PIB, una "
            "tasa de cambio logarítmica que puede interpretarse como una variación porcentual "
            "aproximada del producto interno bruto entre períodos. Un valor positivo sugiere "
            "expansión económica y un valor negativo sugiere contracción; por ejemplo, 0.03 "
            "equivale aproximadamente a un crecimiento de 3%."
        ),
        "version": "1.0.0",
        "trained_at": "2025-06-15",
        "target_variable": "delta_ln_PIB",
        "variables": [
            "delta_ln_EXP",
            "delta_ln_IMP",
            "delta_ln_REM",
            "delta_ln_INV",
            "delta_ln_EMP",
        ],
    },
    {
        "name": "unemployment",
        "display_name": "Determinantes de la Tasa de Desempleo en Pereira A.M.",
        "description": (
            "Estima cómo podría variar la tasa de desempleo del Área Metropolitana de Pereira "
            "ante cambios en la actividad económica, el comercio exterior, las condiciones "
            "sociales y la competitividad territorial. El output es Δln TD, una tasa de cambio "
            "logarítmica de la tasa de desempleo. Valores positivos indican presión al alza "
            "sobre el desempleo y valores negativos indican una reducción esperada. La lectura "
            "debe hacerse como variación porcentual aproximada de la tasa, no como puntos "
            "porcentuales absolutos."
        ),
        "version": "1.0.0",
        "trained_at": "2025-06-15",
        "target_variable": "delta_ln_TD",
        "variables": [
            "delta_ln_PIB",
            "delta_ln_EXP",
            "delta_ln_IMP",
            "IPM",
            "IDC",
        ],
    },
    {
        "name": "business_growth",
        "display_name": "Determinantes del Crecimiento del Tejido Empresarial",
        "description": (
            "Estima la variación esperada del número de empresas activas en Pereira usando "
            "señales de dinamismo económico, demanda externa y liquidez de los hogares vía "
            "remesas. El resultado es Δln EMP, una tasa de cambio logarítmica del tejido "
            "empresarial. Un valor positivo sugiere aumento en el número de empresas y un "
            "valor negativo sugiere contracción empresarial; por ejemplo, 0.04 puede leerse "
            "como un crecimiento aproximado de 4% en empresas activas."
        ),
        "version": "1.0.0",
        "trained_at": "2025-06-15",
        "target_variable": "delta_ln_EMP",
        "variables": [
            "delta_ln_PIB",
            "delta_ln_EXP",
            "delta_ln_REM",
        ],
    },
]

VARIABLES_DATA = {
    "delta_ln_EXP": {
        "display_name": "Crecimiento de exportaciones",
        "description": (
            "Representa la variación relativa de las exportaciones FOB entre dos períodos. "
            "Captura cambios en la demanda externa y en la capacidad local de vender bienes "
            "o servicios fuera del país."
        ),
        "meaning": (
            "Δln(EXP) es una tasa de cambio logarítmica. Para la UI debe leerse como una "
            "variación porcentual aproximada: 0.05 equivale aproximadamente a +5% y -0.05 "
            "a -5% en exportaciones frente al período anterior."
        ),
        "value_type": "log_change_rate",
        "default_value": 0.05,
        "min_value": -0.50,
        "max_value": 0.50,
        "step": 0.01,
    },
    "delta_ln_IMP": {
        "display_name": "Crecimiento de importaciones",
        "description": (
            "Mide la variación relativa de las importaciones CIF. Sirve como proxy de demanda "
            "interna, abastecimiento productivo y consumo de bienes externos."
        ),
        "meaning": (
            "Δln(IMP) es una tasa de cambio logarítmica interpretable como porcentaje "
            "aproximado. Un valor de 0.03 indica cerca de +3% en importaciones; un valor "
            "negativo indica caída relativa."
        ),
        "value_type": "log_change_rate",
        "default_value": 0.03,
        "min_value": -0.50,
        "max_value": 0.50,
        "step": 0.01,
    },
    "delta_ln_REM": {
        "display_name": "Crecimiento de remesas",
        "description": (
            "Resume el cambio relativo en las remesas recibidas por los hogares. Es una señal "
            "de ingreso externo disponible para consumo, ahorro o inversión local."
        ),
        "meaning": (
            "Δln(REM) es una tasa de cambio logarítmica. En la interfaz puede presentarse "
            "como variación porcentual aproximada: 0.02 significa alrededor de +2% en remesas "
            "recibidas entre períodos."
        ),
        "value_type": "log_change_rate",
        "default_value": 0.02,
        "min_value": -0.50,
        "max_value": 0.50,
        "step": 0.01,
    },
    "delta_ln_INV": {
        "display_name": "Crecimiento de inversión neta",
        "description": (
            "Indica la variación relativa de la inversión neta en sociedades. Refleja cambios "
            "en formación de capital, ampliación de empresas y expectativas de actividad "
            "productiva."
        ),
        "meaning": (
            "Δln(INV) es una tasa de cambio logarítmica. Debe interpretarse como variación "
            "porcentual aproximada de la inversión neta: 0.10 representa cerca de +10%, "
            "mientras -0.10 representa cerca de -10%."
        ),
        "value_type": "log_change_rate",
        "default_value": 0.01,
        "min_value": -1.00,
        "max_value": 1.00,
        "step": 0.01,
    },
    "delta_ln_EMP": {
        "display_name": "Crecimiento de empresas activas",
        "description": (
            "Mide la variación relativa del total de empresas activas. Describe la expansión "
            "o contracción del tejido empresarial formal en el territorio."
        ),
        "meaning": (
            "Δln(EMP) es una tasa de cambio logarítmica. Se interpreta como variación "
            "porcentual aproximada del número de empresas: 0.04 equivale a cerca de +4% "
            "y -0.04 a cerca de -4%."
        ),
        "value_type": "log_change_rate",
        "default_value": 0.04,
        "min_value": -0.30,
        "max_value": 0.30,
        "step": 0.01,
    },
    "delta_ln_PIB": {
        "display_name": "Crecimiento del PIB",
        "description": (
            "Representa la variación relativa del producto interno bruto. Resume el cambio "
            "en el nivel agregado de actividad económica usado por los modelos como señal "
            "de expansión o desaceleración."
        ),
        "meaning": (
            "Δln(PIB) es una tasa de cambio logarítmica interpretable como porcentaje "
            "aproximado. Un valor de 0.07 indica cerca de +7% de crecimiento del PIB; "
            "un valor negativo indica contracción relativa."
        ),
        "value_type": "log_change_rate",
        "default_value": 0.07,
        "min_value": -0.30,
        "max_value": 0.30,
        "step": 0.01,
    },
    "IPM": {
        "display_name": "Pobreza multidimensional",
        "description": (
            "Indica la proporción de población en condición de pobreza multidimensional. "
            "Integra privaciones en dimensiones como educación, salud, trabajo, niñez y "
            "condiciones de vivienda."
        ),
        "meaning": (
            "IPM es un porcentaje directo de población. A diferencia de las variables Δln, "
            "no es una tasa logarítmica: 15.0 significa 15% de la población en pobreza "
            "multidimensional."
        ),
        "value_type": "percentage",
        "default_value": 15.0,
        "min_value": 0.0,
        "max_value": 60.0,
        "step": 0.5,
    },
    "IDC": {
        "display_name": "Competitividad departamental",
        "description": (
            "Resume el desempeño competitivo territorial mediante un índice compuesto. "
            "Valores más altos reflejan mejores condiciones relativas en capacidades "
            "productivas, institucionales, infraestructura y entorno para hacer negocios."
        ),
        "meaning": (
            "IDC es un índice numérico normalizado, no un porcentaje. En esta escala, 0 "
            "representa menor competitividad relativa y 10 mayor competitividad relativa."
        ),
        "value_type": "normalized_index",
        "default_value": 5.5,
        "min_value": 0.0,
        "max_value": 10.0,
        "step": 0.1,
    },
}


def _ensure_variable_metadata_columns(db: Session) -> None:
    """Add new metadata columns to an existing SQLite variables table."""
    # SQLite cannot add several columns in one ALTER TABLE statement, so each
    # backward-compatible metadata column is checked and added independently.
    existing_columns = {
        row[1] for row in db.execute(text("PRAGMA table_info(variables)")).all()
    }

    if "display_name" not in existing_columns:
        db.execute(
            text(
                "ALTER TABLE variables ADD COLUMN display_name VARCHAR(200) "
                "DEFAULT '' NOT NULL"
            )
        )
    if "value_type" not in existing_columns:
        db.execute(
            text(
                "ALTER TABLE variables ADD COLUMN value_type VARCHAR(100) "
                "DEFAULT 'standardized_numeric' NOT NULL"
            )
        )
    db.commit()


def seed_database(db: Session) -> None:
    """Create or update the initial model catalog and variable metadata."""
    _ensure_variable_metadata_columns(db)

    variables_map: dict[str, Variable] = {}
    for var_name, var_info in VARIABLES_DATA.items():
        variable = db.query(Variable).filter(Variable.name == var_name).first()
        if variable is None:
            variable = Variable(name=var_name)
            db.add(variable)

        variable.display_name = var_info["display_name"]
        variable.description = var_info["description"]
        variable.meaning = var_info["meaning"]
        variable.value_type = var_info["value_type"]
        variable.default_value = var_info["default_value"]
        variable.min_value = var_info["min_value"]
        variable.max_value = var_info["max_value"]
        variable.step = var_info["step"]
        variables_map[var_name] = variable

    db.flush()

    for model_data in MODELS_DATA:
        model = db.query(EconModel).filter(EconModel.name == model_data["name"]).first()
        if model is None:
            model = EconModel(name=model_data["name"])
            db.add(model)

        model.display_name = model_data["display_name"]
        model.description = model_data["description"]
        model.version = model_data["version"]
        model.trained_at = model_data["trained_at"]
        model.target_variable = model_data["target_variable"]
        db.flush()

        for var_name in model_data["variables"]:
            # Preserve existing relationship rows so repeated development
            # startups can refresh metadata without duplicating links.
            existing_relation = (
                db.query(ModelVariable)
                .filter(
                    ModelVariable.model_id == model.id,
                    ModelVariable.variable_id == variables_map[var_name].id,
                )
                .first()
            )
            if existing_relation is None:
                mv = ModelVariable(
                    model_id=model.id,
                    variable_id=variables_map[var_name].id,
                )
                db.add(mv)

    db.commit()
