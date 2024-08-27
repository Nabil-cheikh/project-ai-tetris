clean:
	@rm -rf ./data/checkpoints/
	@rm -rf ./data/csv/
	@rm -rf ./data/models/
	@mkdir -p data/checkpoints/ data/csv/ data/models/

run:
	@python -m IA_Tetris.main.py
