
# Python config
PYTHON_VERSION := 3.10
PYTHON_BIN := python$(PYTHON_VERSION)

# Environment config
DEV_VIRT_ENV := .venv-dev

# sources
SRC_DIR := swordle
SRC_FILES := $(shell find "$(SRC_DIR)" -type f -name "*.py")

# Virtual environment targets
$(DEV_VIRT_ENV):
	$(PYTHON_BIN) -m venv "$@"
	. "$@/bin/activate"; \
	pip install --upgrade pip
	touch "$@"

.PHONY: setup-dev
setup-dev: $(DEV_VIRT_ENV) pyproject.toml setup.cfg $(SRC_DIR) .pre-commit-config.yaml
	. "$(DEV_VIRT_ENV)/bin/activate"; \
	pip install -e .[dev]


# clean up target
.PHONY: clean
clean:
	rm -rf \
		$(DEV_VIRT_ENV) \
		$(shell find $(SRC_DIR) -type f -name *.pyc) \
		$(shell find $(SRC_DIR) -type d -name *.egg-info) \
		.mypy_cache/ \
		build/