
# --------------------------------------------------
# -------------------- odoo ------------------------
# --------------------------------------------------
docker_template = """
%(docker_command)s run -p 127.0.0.1:%(erp_port)s:8069 -p 127.0.0.1:%(erp_longpoll)s:8072 --restart always \
    -v %(erp_server_data_path)s/%(site_name)s/etc:/etc/odoo \
    -v %(erp_server_data_path)s/%(site_name)s/start-entrypoint.d:/opt/odoo/start-entrypoint.d \
    -v %(erp_server_data_path)s/%(site_name)s/addons:/mnt/extra-addons \
    -v %(erp_server_data_path)s/%(site_name)s/dump:/mnt/dump \
    -v %(erp_server_data_path)s/%(site_name)s/filestore:/var/lib/odoo/filestore \
    -v %(erp_server_data_path)s/%(site_name)s/:/var/lib/odoo/ \
    -v %(erp_server_data_path)s/%(site_name)s/log:/var/log/odoo \
    -e LOCAL_USER_ID=1000 -e DB_NAME=%(site_name)s \
    -e PYTHONIOENCODING=utf-8 \
    --name %(container_name)s -d --link db:db -t %(erp_image_version)s
"""
# for docker_template_update I changed:
# --restart always -> --rm
# -d -> ''
# -> --init /etc/odoo/runodoo.sh \
docker_template_update = """
%(docker_command)s run -p 127.0.0.1:%(erp_port)s:8069 -p 127.0.0.1:%(erp_longpoll)s:8072 --rm \
    --entrypoint /etc/odoo/runodoo.sh \
    -v %(erp_server_data_path)s/%(site_name)s/etc:/etc/odoo \
    -v %(erp_server_data_path)s/%(site_name)s/start-entrypoint.d:/opt/odoo/start-entrypoint.d \
    -v %(erp_server_data_path)s/%(site_name)s/addons:/mnt/extra-addons \
    -v %(erp_server_data_path)s/%(site_name)s/dump:/mnt/dump \
    -v %(erp_server_data_path)s/%(site_name)s/filestore:/var/lib/odoo/filestore \
    -v %(erp_server_data_path)s/%(site_name)s/:/var/lib/odoo/ \
    -v %(erp_server_data_path)s/%(site_name)s/log:/var/log/odoo \
    -e LOCAL_USER_ID=1000 -e DB_NAME=%(site_name)s \
    -e PYTHONIOENCODING=utf-8 \
    --name %(container_name)s_tmp --link db:db -t %(erp_image_version)s
"""

docker_db_template = """
    %(docker_command)s run -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo \
    -v %(erp_server_data_path)s/database/data:/var/lib/postgresql/data --name db --restart always \
    -p 55432:5432 postgres:%(postgres_version)s
"""

docker_file_template = """
FROM %(erp_base_image)s

# Install dependencies
RUN apt-get update && apt-get install -y \

RUN add-apt-repository universe
RUN apt-get update && apt-get install -y \
    python-pip

RUN pip install %(pip_list)s
"""
docker_run_apt_template = """# Project's specifics packages
RUN set -x; \\
        apt-get update \\
        && apt-get install -y --no-install-recommends \\
        %(apt_list)s \\
        %(pip_install)s %(pip_list)s \\
        && apt-get remove -y \\
        %(apt_list)s \\
        && apt-get clean \\
        && rm -rf /var/lib/apt/lists/*
"""
docker_run_no_apt_template = """# Project's specifics packages
RUN set -x; \\
        %(pip_install)s %(pip_list)s \\
"""

docker_base_file_template = """
FROM %(erp_image_version)s
MAINTAINER robert@redo2oo.ch

# For installing odoo you have two possibility
# 1. either adding the whole root directory
#COPY . /odoo

# 2. or adding each directory, this solution will reduce the build and download
# time of the image on the server (layers are reused)
COPY ./src /odoo/src
COPY ./external-src /odoo/external-src
COPY ./local-src /odoo/local-src
COPY ./data /odoo/data
COPY ./songs /odoo/songs
COPY ./setup.py /odoo/
COPY ./VERSION /odoo/
COPY ./migration.yml /odoo/
RUN pip install --cache-dir=.pip -e /odoo
RUN pip install --cache-dir=.pip -e /odoo/src

%(run_block)s

COPY ./requirements.txt /odoo/
RUN cd /odoo && pip install --cache-dir=.pip -r requirements.txt

ENV ADDONS_PATH=/odoo/local-src,/odoo/src/addons
#ENV DB_NAME=afbsdemo
ENV MIGRATE=False
# Set the default config file
ENV OPENERP_SERVER /etc/odoo/openerp-server.conf
"""
docker_erp_setup_version = """
%s.0
"""
docker_erp_setup_requirements = """
# project's packages, customize for your needs:
unidecode==0.4.14
"""

docker_erp_setup_script = """
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('VERSION') as fd:
    version = fd.read().strip()

setup(
    name="my-project-name",
    version=version,
    description="project description",
    license='GNU Affero General Public License v3 or later (AGPLv3+)',
    author="Author...",
    author_email="email...",
    url="url...",
    packages=['songs'] + ['songs.%s' % p for p in find_packages('./songs')],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved',
        'License :: OSI Approved :: '
        'GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
"""
# --------------------------------------------------
# -------------------- FLECTRA ---------------------
# --------------------------------------------------
flectra_docker_template = """
docker run -p 127.0.0.1:%(erp_port)s:7073 -p 127.0.0.1:%(erp_longpoll)s:7072 --restart always \
    -v %(erp_server_data_path)s/%(site_name)s/etc:/etc/flectra \
    -v %(erp_server_data_path)s/%(site_name)s/addons:/mnt/extra-addons \
    -v %(erp_server_data_path)s/%(site_name)s/dump:/mnt/dump \
    -v %(erp_server_data_path)s/%(site_name)s/filestore:/var/lib/flectra/filestore \
    -v %(erp_server_data_path)s/%(site_name)s/:/var/lib/flectra/ \
    -v %(erp_server_data_path)s/%(site_name)s/log:/var/log/flectra \
    -e LOCAL_USER_ID=1000 -e DB_NAME=%(site_name)s \
    -e PYTHONIOENCODING=utf-8 \
    --name %(container_name)s -d --link db:db -t %(erp_image_version)s
"""

dumper_docker_template = """
# dbdumper Dockerfile 
FROM debian:stretch

RUN apt update; apt install -y wget gnupg; \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - ; \
    sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
RUN apt-get update &&  apt-get install postgresql-client-%(postgres_version)s vim python -y --allow-unauthenticated

ENTRYPOINT ["/usr/bin/python", "/mnt/sites/dumper/dumper.py"]
"""