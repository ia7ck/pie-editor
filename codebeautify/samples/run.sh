mkdir ./src/ -p
cp $OpenXM_HOME/src/asir-contrib/packages/src/*.rr ./src/

mkdir ./dest/ -p
for f in $(ls ./src/*.rr); do
  nkf $f | ../beautifier.py > ./dest/$(basename $f)
  echo $f ... ok
done
