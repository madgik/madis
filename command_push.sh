cd src/docs
./builddocs.sh
cd ../../
cp -r src/docs/html/* .
git add *
git commit -am "update documentation"
git push origin gh-pages
