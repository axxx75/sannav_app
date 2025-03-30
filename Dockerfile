FROM alpine:3.18

# Aggiorna i repository e installa i pacchetti necessari:
# - python3 e py3-pip
# - apache2 e php con modulo Apache per PHP
# - supervisor per gestire i processi
# - crond per eseguire il cron job
RUN apk update && apk add --no-cache \
    php php-cli php-phar php-json php-openssl php-mbstring php-xml php-tokenizer php-session \
    php-curl php-pdo php-pdo_mysql php-mysqli php-gd php-zip php-dom php-ctype \
    apache2 apache2-utils php-apache2 python3 py3-pip py3-virtualenv supervisor sqlite sqlite-libs sqlite-dev curl jq \
    && rm -rf /var/cache/apk/*

# Set TimeZone
RUN apk add --no-cache tzdata
ENV TZ=Europe/Rome
RUN cp /usr/share/zoneinfo/Europe/Rome /etc/localtime

# Installa requirements tramite pip
COPY requirements.txt  /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Configura Apache
COPY httpd.conf /etc/apache2/httpd.conf

# Se necessario, assicurati che il modulo PHP sia abilitato in httpd.conf:
# (in Alpine, la configurazione di PHP viene solitamente inclusa automaticamente tramite i file in /etc/apache2/conf.d/)
# COPY php.conf /etc/apache2/conf.d/php.conf  <-- se volessi forzare la configurazione

# Copia le web page nel document root di Apache (di default in Alpine è /var/www/localhost/htdocs/)
ADD app/ /app
ADD page/ /var/www/localhost/htdocs
RUN ln -s /app/sannav_pg_nodbg.py /app/sannav_pg.py

# Espone la porta: 80 per Apache e la 5001 per Flask
EXPOSE 80
EXPOSE 5001

# Imposta cron 
RUN echo '*/5  *  *  *  * python /app/sannav_pg.py ' >> /etc/crontabs/root
RUN echo '10  *  *  *  * python /app/output_bk.py ' >> /etc/crontabs/root

# Eseguo la Discovery San per partire con dati nuovi e aggiornati
RUN /usr/bin/python -Wi  /app/sannav_pg.py

# Copia il file di configurazione per Supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Avvia Supervisor che gestirà Apache, Flask e il demone cron
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf", "-l", "/var/log/supervisord.log"]
