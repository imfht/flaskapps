.\Scripts\activate
pyinstaller src/wsgi.py -F `
--name "cfe-os-windows" `
--icon='icon.ico' `
--add-data "src\data\*;data" `
--add-data "src\data\*.jpg;data" `
--hidden-import waitress `
--clean