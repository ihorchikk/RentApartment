ve:
	test ! -d .ve && virtualenv -p python3 .ve; \
	. .ve/bin/activate; \
	pip install -r requirements/prod.txt; \

dev:
	test ! -d .ve && virtualenv -p python3 .ve; \
	. .ve/bin/activate; \
	pip install -r requirements/prod.txt; \
	pip install -r requirements/ci.txt

clean:
	test -d .ve && rm -rf .ve