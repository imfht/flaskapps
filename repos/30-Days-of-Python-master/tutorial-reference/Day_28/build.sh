source bin/activate
pyinstaller src/wsgi.py -F \
--name "cfe-os-mac" \
--icon='icon.icns' \
--add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk' \
--add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl' \
--add-data "src/data/*:data" \
--add-data "src/data/*.jpg:data" \
--hidden-import waitress \
--clean