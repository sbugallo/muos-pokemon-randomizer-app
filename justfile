alias c := clean
alias b := build
alias z := zip

default: clean build
muxapp: clean build zip

clean:
	@echo "Cleaning..."
	rm -rf .build
	rm -rf .dist

base_name := "Pokemon-Randomizer-Installer"
version := `
	bash -c 'VERSION=$(grep -o "\"[^\"]*\"" src/__version__.py | tr -d "\"")
	VERSION=${VERSION//\//_}
	echo ${VERSION}'
`

build: 
	@echo "Downloading Universal Pokemon Randomizer ZX v4.6.1..."

	mkdir -p src/3rd-party
	wget https://github.com/Ajarmar/universal-pokemon-randomizer-zx/releases/download/v4.6.1/PokeRandoZX-v4_6_1.zip -O randomizer.zip
	unzip -j randomizer.zip PokeRandoZX.jar -d src/3rd-party/
	rm randomizer.zip

	@echo "Building Pokemon Randomizer..."

	mkdir -p .build
	rsync -a --exclude={__pycache__,.venv,.env,.DS_Store,.build,.dist} src/ '.build/Pokemon Randomizer/'

	@echo "Copying Python dependencies..."

	cp requirements.txt .build/requirements.txt
	python -m pip install --upgrade pip
	python -m pip install --no-cache-dir --platform manylinux_2_28_aarch64 --only-binary=:all: --implementation cp -r .build/requirements.txt --upgrade --target='.build/Pokemon Randomizer/deps'
	rm .build/requirements.txt

	# Move pillow libs to the right place
	mv '.build/Pokemon Randomizer/deps/pillow.libs' '.build/Pokemon Randomizer/libs'

	# Remove unnecessary files
	find '.build/Pokemon Randomizer/deps' -name "*.dist-info" -type d -exec rm -rf {} \; 2>/dev/null || true
	find '.build/Pokemon Randomizer/deps' -name "*__pycache__" -type d -exec rm -rf {} \; 2>/dev/null || true
	rm -r '.build/Pokemon Randomizer/deps/sdl2/examples' 
	rm -r '.build/Pokemon Randomizer/deps/sdl2/test'

zip:
	mkdir -p .dist
	cd .build && zip -r "{{ base_name }}-{{ version }}.muxapp" ./*
	mv ".build/{{ base_name }}-{{ version }}.muxapp" ".dist/{{ base_name }}-{{ version }}.muxapp"
