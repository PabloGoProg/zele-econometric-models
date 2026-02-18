"""Seed de datos iniciales: modelos econométricos y sus variables."""

from sqlalchemy.orm import Session

from src.models.entities import EconModel, ModelVariable, Variable

MODELS_DATA = [
    {
        "name": "econ_growth",
        "description": (
            "Determinantes del Crecimiento Económico de Pereira. "
            "Predice la tasa de crecimiento del PIB (Δln PIB) a partir de "
            "exportaciones, importaciones, remesas, inversión y número de empresas."
        ),
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
        "description": (
            "Determinantes de la Tasa de Desempleo en Pereira A.M. "
            "Predice la variación de la tasa de desempleo (Δln TD) a partir del "
            "crecimiento del PIB, exportaciones, importaciones, pobreza "
            "multidimensional y competitividad departamental."
        ),
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
        "description": (
            "Determinantes del Crecimiento del Tejido Empresarial. "
            "Predice la variación del número de empresas (Δln EMP) a partir del "
            "crecimiento del PIB, exportaciones y remesas."
        ),
        "variables": [
            "delta_ln_PIB",
            "delta_ln_EXP",
            "delta_ln_REM",
        ],
    },
]

VARIABLES_DATA = {
    "delta_ln_EXP": {
        "description": "Tasa de cambio logarítmica de las exportaciones",
        "meaning": "Δln(EXP): Variación porcentual aproximada de las exportaciones FOB entre períodos",
        "default_value": 0.05,
    },
    "delta_ln_IMP": {
        "description": "Tasa de cambio logarítmica de las importaciones",
        "meaning": "Δln(IMP): Variación porcentual aproximada de las importaciones CIF entre períodos",
        "default_value": 0.03,
    },
    "delta_ln_REM": {
        "description": "Tasa de cambio logarítmica de las remesas",
        "meaning": "Δln(REM): Variación porcentual aproximada de las remesas recibidas entre períodos",
        "default_value": 0.02,
    },
    "delta_ln_INV": {
        "description": "Tasa de cambio logarítmica de la inversión neta",
        "meaning": "Δln(INV): Variación porcentual aproximada de la inversión neta en sociedades entre períodos",
        "default_value": 0.01,
    },
    "delta_ln_EMP": {
        "description": "Tasa de cambio logarítmica del número de empresas",
        "meaning": "Δln(EMP): Variación porcentual aproximada del total de empresas activas entre períodos",
        "default_value": 0.04,
    },
    "delta_ln_PIB": {
        "description": "Tasa de cambio logarítmica del PIB",
        "meaning": "Δln(PIB): Variación porcentual aproximada del PIB a precios corrientes entre períodos",
        "default_value": 0.07,
    },
    "IPM": {
        "description": "Incidencia de Pobreza Multidimensional de Risaralda",
        "meaning": "IPM: Porcentaje de la población en situación de pobreza multidimensional",
        "default_value": 15.0,
    },
    "IDC": {
        "description": "Índice de Competitividad Departamental (valor normalizado)",
        "meaning": "IDC: Indicador compuesto de competitividad territorial de Risaralda",
        "default_value": 5.5,
    },
}


def seed_database(db: Session) -> None:
    """Pobla la base de datos con los modelos y variables iniciales si están vacíos."""
    if db.query(EconModel).first() is not None:
        return

    variables_map: dict[str, Variable] = {}
    for var_name, var_info in VARIABLES_DATA.items():
        variable = Variable(
            name=var_name,
            description=var_info["description"],
            meaning=var_info["meaning"],
            default_value=var_info["default_value"],
        )
        db.add(variable)
        variables_map[var_name] = variable

    db.flush()

    for model_data in MODELS_DATA:
        model = EconModel(
            name=model_data["name"],
            description=model_data["description"],
        )
        db.add(model)
        db.flush()

        for var_name in model_data["variables"]:
            mv = ModelVariable(
                model_id=model.id,
                variable_id=variables_map[var_name].id,
            )
            db.add(mv)

    db.commit()
