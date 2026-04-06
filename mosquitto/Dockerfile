# Imagen Mosquitto con generación de passwd en runtime.
# Funciona tanto en desarrollo local como en Dokploy/producción.
FROM eclipse-mosquitto:2.0.21

COPY mosquitto.conf /mosquitto/config/mosquitto.conf
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
