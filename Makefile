tailwind:
	tailwindcss -i static/tailwind.css -o static/styles.css

tailwind-watch:
	tailwindcss -i static/tailwind.css -o static/styles.css --watch

install-local:
	pip uninstall -y volt-framework
	pip install -e ../volt --config-settings editable_mode=strict
