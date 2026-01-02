# API

## Personas

### GET (/api/persona)

Requiere al menos uno de los parámetros `correo` o `acreditacion`.

Muestra detalles de las Personas que cumplen los requisitos.

### PATCH (/api/persona/\<correo\>/)

Asigna una acreditación a un participante.

Body:

```json
{
    "acreditacion": "<valor>"
}
```

## Tipos de Pase

### GET (/api/tipo_pase)

Muestra los tipos de pase creados con sus propiedades.

Ordenados por fecha de inicio de validez, los más antiguos primero.

## Pases

### GET (/api/pase)

Muestra los pases creados.

Admite el parámetro `persona` para filtrar por correo.

Ordenados por fecha, los más recientes primero

### GET (/api/pase/\<id_pase\>)

Muestra el pase concreto.

### POST (/api/pase)

Crea un pase.

Body:

```json
{
    "persona": "<correo>",
    "tipo_pase": "<id_tipo_pase>"
}
```

## Presencias

### GET (/api/presencia)

Mostrar todas las presencias.

Admite el parámetro `persona` para filtrar por correo.

Ordenados por `entrada`, los más recientes primero.

> Nota:
> Los pases con `entrada` nula aparecen al final.

### GET (/api/presencia/\<id_presencia\>)

Muestra la presencia concreta.

### POST (/api/presencia)

Crea una presencia.

Body:

```json
{
    "persona": "<correo>",
    "entrada": "<fechahorazona>",
    "salida": "<fechahorazona>"
}
```

> Notas:
>
> - `entrada` y `salida` deben ser un string en ISO 8601 válido o bien `null`.

### PATCH (/api/presencia/\<id_presencia\>)

Modifica una presencia.

Body:

```json
{
    "persona": "<correo>",
    "entrada": "<fechahorazona>",
    "salida": "<fechahorazona>"
}
```

> Notas:
>
> - No es necesario incluir los 3 atributos. Incluir solo los que se quieran modificar.
> - `entrada` y `salida` deben ser un string en ISO 8601 válido o bien `null`.
