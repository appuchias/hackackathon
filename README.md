# Hackackathon

Un proyecto hecho con Django para la gestión de hackackatones.


# Diagrama Entidad-Relación de los modelos empleados

```mermaid
erDiagram

    PERSONAABSTRACTA {
        string correo PK
        string nombre
        text notas
        string acreditacion
    }

    PATROCINADOR {
        string correo PK, FK
        string empresa
    }

    PERSONA {
        string correo PK, FK
        string dni
        string genero
        string talla_camiseta
        file cv
        bool compartir_cv
        datetime fecha_registro
        datetime fecha_verificacion_correo
        datetime fecha_aceptacion
        datetime fecha_confirmacion_plaza
    }

    MENTOR {
        string correo PK, FK
    }

    PARTICIPANTE {
        string correo PK, FK
        string telefono
        int ano_nacimiento
        string nivel_estudio
        string nombre_estudio
        string centro_estudio
        string curso
        string ciudad
        bool quiere_creditos
        text motivacion
    }

    RESTRICCIONALIMENTARIA {
        int id_restriccion PK
        string nombre
    }

    PRESENCIA {
        int id_presencia PK
        datetime entrada
        datetime salida
        string persona_id FK
    }

    TIPOPASE {
        int id_tipo_pase PK
        string nombre
        datetime inicio_validez
    }

    PASE {
        int id_pase PK
        string persona_id FK
        int tipo_pase_id FK
        datetime fecha
    }

    TOKEN {
        uuid token PK
        string tipo
        string persona_id FK
        datetime fecha_creacion
        datetime fecha_expiracion
        datetime fecha_uso
    }

    %% Relaciones
    PERSONAABSTRACTA ||--o{ RESTRICCIONALIMENTARIA : "restricciones_alimentarias"
    PERSONA ||--o{ PRESENCIA : "tiempo_acceso"
    PERSONA ||--o{ PASE : "pases"
    PERSONA ||--o{ TOKEN : "tokens"

    TIPOPASE ||--o{ PASE : "pases"

    %% Herencia
    PERSONAABSTRACTA ||--|{ PERSONA : ""
    PERSONAABSTRACTA ||--|{ PATROCINADOR : ""
    PERSONA ||--|{ MENTOR : ""
    PERSONA ||--|{ PARTICIPANTE : ""
```


## Licencia

El proyecto está bajo la licencia AGPLv3, para más info ver [la licencia](LICENSE).
