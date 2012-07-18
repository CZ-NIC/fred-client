#!/bin/bash

case $1 in

    'make')

    echo -n 'FORMS = '
    find . -name '*.ui' -printf '%P '
    echo ''

    echo -n 'SOURCES = '
    find . ! -name 'ui_*.*' -name '*.py' -printf '%P '
    echo ''

    echo -n 'TRANSLATIONS = '
    find . -name '*.ts' -printf '%P '
    echo ''
    ;;

    *)
    echo "Usage: sh make_project make > file.project"
    ;;
esac
