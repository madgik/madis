git checkout gh-pages
python src/docs/generate_fuction_doc.py
./src/docs/builddocs.sh
touch .no
cp src/docs/html/* .
git commit -am "update documentation"
git push origin gh-pages
git checkout master
git push origin master
