.PHONY: data run

data: api/GPTree.cpp
	mkdir -p build
	g++ -std=c++11 -O3 -lmetis -o build/GPTree api/GPTree.cpp
	./build/GPTree load

run:
	python backend/work.py

