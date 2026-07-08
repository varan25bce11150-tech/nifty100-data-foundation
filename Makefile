load:
	python src/etl/loader.py

test:
	pytest tests/

report:
	python src/etl/validator.py

clean:
	del nifty100.db