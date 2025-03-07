echo "<!DOCTYPE html>"
echo "<html>"

cat src/head.html

echo "<body>"
pandoc -f markdown-smart -t html src/index.md
cat src/footer.html
echo "</body>"

echo "</html>"
