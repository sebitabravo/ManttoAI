# Imagen Mosquitto con generación de passwd en runtime.
# Funciona tanto en desarrollo local como en Dokploy/producción.
FROM eclipse-mosquitto:2.0.21

COPY mosquitto.conf /mosquitto/config/mosquitto.conf
COPY docker-entrypoint.sh /docker-entrypoint.sh
# La fuente puede llegar con modo 0600 desde macOS; el shell del usuario
# mosquitto necesita poder leer y ejecutar el script dentro del contenedor.
RUN chmod 755 /docker-entrypoint.sh
# Establecer permisos correctos durante la construcción de la imagen
RUN chown -R mosquitto:mosquitto /mosquitto
# Forzar el usuario mosquitto (UID 1883) para todo el runtime
USER mosquitto:mosquitto

ENTRYPOINT ["/docker-entrypoint.sh"]
