#!/bin/sh

export CORREO_ORIGINAL=$1
export CORREO_NUEVO=$2

# Comprobar que no estén vacíos
if [ -z "$CORREO_ORIGINAL" ] || [ -z "$CORREO_NUEVO" ]; then
  echo "ERROR: Ambos valores deben ser proporcionados."
  echo "Uso: $0 <correo_original> <correo_nuevo>"
  exit 1
fi

echo "Correo original: $CORREO_ORIGINAL"
echo "Correo nuevo: $CORREO_NUEVO"

echo -n "Personas con el correo original: "
sqlite3 -ifexists db.sqlite3 "SELECT count(*) FROM gestion_persona WHERE correo='$CORREO_ORIGINAL';"
echo -n "Personas con el correo nuevo: "
sqlite3 -ifexists db.sqlite3 "SELECT count(*) FROM gestion_persona WHERE correo='$CORREO_NUEVO';"

printf "\n¿Modificar BD? (Y/n) "
read -r RESPUESTA
RESPUESTA_LOWER=$(echo "$RESPUESTA" | tr '[:upper:]' '[:lower:]')

# Comprobar la respuesta
if [ -z "$RESPUESTA" ] || [ "$RESPUESTA_LOWER" = "y" ]; then
  echo "
  BEGIN TRANSACTION;
  UPDATE OR ROLLBACK gestion_persona SET correo='$CORREO_NUEVO' WHERE correo='$CORREO_ORIGINAL';
  SELECT 'Personas actualizadas: ' || changes();
  UPDATE OR ROLLBACK gestion_participante SET persona_ptr_id='$CORREO_NUEVO' where persona_ptr_id='$CORREO_ORIGINAL';
  SELECT 'Participantes actualizados: ' || changes();
  UPDATE OR ROLLBACK gestion_token SET persona_id='$CORREO_NUEVO' where persona_id='$CORREO_ORIGINAL';
  SELECT 'Tokens actualizados: ' || changes();
  COMMIT;
  " | sqlite3 -ifexists db.sqlite3
elif [ "$RESPUESTA_LOWER" = "n" ]; then
  echo "No se ha modificado la BD"
  exit 0
else
  echo "Entrada no válida"
  exit 1
fi
