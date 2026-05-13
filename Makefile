APP_NAME = screensheet
PREFIX ?= /usr/local
BINDIR = $(PREFIX)/bin
DATADIR = $(PREFIX)/share
APPDIR = $(DATADIR)/applications
ICONDIR = $(DATADIR)/icons/hicolor/scalable/apps
PYDIR = $(DATADIR)/$(APP_NAME)

PYTHON = python3

.PHONY: all install uninstall clean run

all:
	@echo "Run 'make install' to install $(APP_NAME) to $(PREFIX)"
	@echo "Run 'make run' to start the application"
	@echo "Run 'make uninstall' to remove the application"

install:
	@echo "Installing $(APP_NAME)..."
	@mkdir -p $(DESTDIR)$(BINDIR)
	@mkdir -p $(DESTDIR)$(APPDIR)
	@mkdir -p $(DESTDIR)$(ICONDIR)
	@mkdir -p $(DESTDIR)$(PYDIR)
	@cp -r src $(DESTDIR)$(PYDIR)/
	@cp screensheet.py $(DESTDIR)$(PYDIR)/
	@sed 's|Exec=screensheet|Exec=$(PYTHON) $(PYDIR)/screensheet.py|;s|Icon=screensheet|Icon=$(APP_NAME)|' data/$(APP_NAME).desktop > $(DESTDIR)$(APPDIR)/$(APP_NAME).desktop
	@cp data/icons/$(APP_NAME).svg $(DESTDIR)$(ICONDIR)/
	@chmod +x $(DESTDIR)$(PYDIR)/screensheet.py
	@echo '#!/bin/sh' > $(DESTDIR)$(BINDIR)/$(APP_NAME)
	@echo 'exec $(PYTHON) $(PYDIR)/screensheet.py "$$@"' >> $(DESTDIR)$(BINDIR)/$(APP_NAME)
	@chmod +x $(DESTDIR)$(BINDIR)/$(APP_NAME)
	@echo "Installation complete!"

uninstall:
	@echo "Uninstalling $(APP_NAME)..."
	@rm -f $(DESTDIR)$(BINDIR)/$(APP_NAME)
	@rm -f $(DESTDIR)$(APPDIR)/$(APP_NAME).desktop
	@rm -f $(DESTDIR)$(ICONDIR)/$(APP_NAME).svg
	@rm -rf $(DESTDIR)$(PYDIR)
	@echo "Uninstallation complete!"

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete 2>/dev/null || true
	@echo "Cleaned."

run:
	$(PYTHON) screensheet.py
