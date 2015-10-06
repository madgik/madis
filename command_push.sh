git checkout gh-pages
cd src/docs
./builddocs.sh
cd ../../
cp src/docs/html/* .
git commit -am "update documentation"
git push origin gh-pages
git checkout master
