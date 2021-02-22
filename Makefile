VENV=.venv

start:
	. ${VENV}/bin/activate; uvicorn main:app --reload

init:
	python -m venv ${VENV}
	${MAKE} upgrade-pip
	${MAKE} install-dev

prod-init:
	pip install --upgrade pip; ${MAKE} install

upgrade-pip:
	. ${VENV}/bin/activate; pip install --upgrade pip

install:
	pip install -r requirements.txt

install-dev:
	. ${VENV}/bin/activate; $(MAKE) install; pip install -r requirements-dev.txt

clean:
	rm -rf ${VENV}
	find . -iname "*.pyc" -delete


.PHONY: start install install-devinit prod-init upgrade-pip clean