# Guía rápida sobre traducciones

> [!IMPORTANT]\
> La documentación oficial está disponible [aquí](https://docs.djangoproject.com/en/5.2/topics/i18n/translation/).\
> Personalmente recomiendo leer al menos hasta la sección de `Lazy Translation` (incluida).

> [!IMPORTANT]\
> No queremos traducciones hechas por IA.
> Valoramos el trabajo humano y preferimos no disponer de las traducciones de un idioma antes que servir traducciones
> hechas por IA.\
> **Por favor, abstente de realizar contribuciones que no sean de autoría humana.**

## Procedimiento de traducción

### Modificación del código o las plantillas para integrar las traducciones

(Solo necesario la primera vez que se traduce un archivo)

#### En Python

Se introduce el texto a traducir en la llamada a la función `_()`, definida de forma distinta en función de qué archivo
se trate:

- En archivos habituales,\
  `from django.utils.translation import gettext as _`.\
- En archivos ejecutados en el arranque de Django (`admin.py`, `settings.py`, etc.)
  https://docs.djangoproject.com/en/5.2/topics/i18n/translation/#lazy-translation \
  `from django.utils.translation import gettext_lazy as _`
- En casos en los que el texto a traducir requiera contexto (aparece en varias situaciones con traducciones distintas),
  emplear las variantes:\
  https://docs.djangoproject.com/en/5.2/topics/i18n/translation/#contextual-markers \
  `from django.utils.translation import pgettext as _` y\
  `from django.utils.translation import pgettext_lazy as _`\
  como `_("<contexto>", "<texto a traducir>")`
- En traducciones que requieran plurales, usar las variantes:\
  https://docs.djangoproject.com/en/5.2/topics/i18n/translation/#pluralization \
  `from django.utils.translation import ngettext` y\
  `from django.utils.translation import ngettext`.
  Para más detalles de su uso ver la documentación oficial.

Para aportar contexto adicional a los traductores, se debe añadir un comentario en la línea previa a la llamada con la
estructura siguiente:
`# Translators: <el comentario>`

#### En plantillas

Se introduce el texto a traducir entre las comillas de `{% translate '' %}`.

Para aportar contexto adicional a los traductores, se debe añadir un comentario en la línea previa a la llamada con la
estructura siguiente:
`{# Translators: <el comentario> #}`

### Creación del archivo de traducción

`python manage.py makemessages --all`

### Traducción de los archivos generados

Se deberán traducir los archivos presentes en `locale/*/*.po`.

### Compilación de las traducciones para su uso

`python manage.py compilemessages`

> Esto es solo un resumen rápido.
> Para información detallada *recomiendo muy encarecidamente* leer la documentación oficial.
> Hay muchos matices que no están recogidos en este documento, bien por desconocimiento, bien por no extenderse en
> exceso.
