echo "\
<!DOCTYPE html>
<html>
"

cat src/head.html

echo "\
  <body>
    <div class='indexcontainer'>
      <div class='container'>
"

pandoc -f markdown-smart -t html src/index.md
cat src/footer.html

echo "\
      </div>
    </div>
  </body>
</html>
"
