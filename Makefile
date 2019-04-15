mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))
ROOT_DIR := $(dir $(mkfile_path))
AWS_ZIP_FILE := deploy_lambda_function.zip
VIRTUAL_ENV_AWS := virtualenv

.PHONY : help

all : build

clean: clean_build

build: build_sensor build_context build_reaction

build_sensor : clean ## generate zip file to deploy lambda
		mkdir -p build_sensor/site-packages
		zip -r build_sensor/$(AWS_ZIP_FILE) . -x "*contelog*" "*virtual*" "*.git*" "build*" "Makefile" "build_requirements.txt" "*.vscode*" "context_lambda_function.py" "reaction_lambda_function.py"
		virtualenv -p python3 build_sensor/$(VIRTUAL_ENV_AWS)
		. build_sensor/$(VIRTUAL_ENV_AWS)/bin/activate; \
		pip3 install -r build_requirements.txt; \
		cp -r $$VIRTUAL_ENV/lib/python3.5/site-packages/ build_sensor/site-packages
		cd build_sensor/site-packages; zip -g -r ../$(AWS_ZIP_FILE) . -x "*__pycache__*"

build_context : clean ## generate zip file to deploy lambda
		mkdir -p build_context/site-packages
		chmod 775 contelog/*
		zip -r build_context/$(AWS_ZIP_FILE) . -x "*virtual*" "*.git*" "build*" "Makefile" "build_requirements.txt" "*.vscode*" "sensor_lambda_function.py" "reaction_lambda_function.py"
		virtualenv -p python3 build_context/$(VIRTUAL_ENV_AWS)
		. build_context/$(VIRTUAL_ENV_AWS)/bin/activate; \
		pip3 install -r build_requirements.txt; \
		cp -r $$VIRTUAL_ENV/lib/python3.5/site-packages/ build_context/site-packages
		cd build_context/site-packages; zip -g -r ../$(AWS_ZIP_FILE) . -x "*__pycache__*"

build_inference : clean ## generate zip file to deploy lambda
		mkdir -p build_inference/site-packages
		chmod 775 contelog/*
		zip -r build_inference/$(AWS_ZIP_FILE) . -x "*virtual*" "*.git*" "build*" "Makefile" "build_requirements.txt" "*.vscode*" "context_lambda_function.py" "sensor_lambda_function.py" "reaction_lambda_function.py"
		virtualenv -p python3 build_inference/$(VIRTUAL_ENV_AWS)
		. build_inference/$(VIRTUAL_ENV_AWS)/bin/activate; \
		pip3 install -r build_requirements.txt; \
		cp -r $$VIRTUAL_ENV/lib/python3.5/site-packages/ build_inference/site-packages
		cd build_inference/site-packages; zip -g -r ../$(AWS_ZIP_FILE) . -x "*__pycache__*"

build_reaction : clean ## generate zip file to deploy lambda
		mkdir -p build_reaction/site-packages
		zip -r build_reaction/$(AWS_ZIP_FILE) . -x "*contelog*" "*virtual*" "*.git*" "build*" "Makefile" "build_requirements.txt" "*.vscode*" "context_lambda_function.py" "sensor_lambda_function.py"
		virtualenv -p python3 build_reaction/$(VIRTUAL_ENV_AWS)
		. build_reaction/$(VIRTUAL_ENV_AWS)/bin/activate; \
		pip3 install -r build_requirements.txt; \
		cp -r $$VIRTUAL_ENV/lib/python3.5/site-packages/ build_reaction/site-packages
		cd build_reaction/site-packages; zip -g -r ../$(AWS_ZIP_FILE) . -x "*__pycache__*"

clean_build : ## cleans the build env
	rm -rf build_sensor
	rm -rf build_context
	rm -rf build_reaction
	rm -rf build_inference