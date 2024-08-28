clear_directories:
	@mkdir -p data/checkpoints/ data/csv/ data/models/

clean:
	@rm -rf ./data/checkpoints/
	@rm -rf ./data/csv/
	@rm -rf ./data/models/
	@make clear_directories

run:
	@python -m IA_Tetris.main
