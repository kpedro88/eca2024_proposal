#!/bin/bash -e

ECHO="echo -e"

run_pdflatex(){
pdflatex -interaction=nonstopmode -synctex=-1 "$1.tex" > "$1.log" 2>&1
}

SOURCE=main
$ECHO "refcheck\n"
python refcheck.py -q biblio.tex ${SOURCE}.tex
$ECHO "First pass\n"
run_pdflatex $SOURCE
#$ECHO "bibtex"
#bibtex "$SOURCE.aux"
$ECHO "\nSecond pass\n"
run_pdflatex $SOURCE
#$ECHO "Third pass\n"
#run_pdflatex $SOURCE
$ECHO "Renaming"
mv ${SOURCE}.pdf proposal.pdf
$ECHO "Done"

