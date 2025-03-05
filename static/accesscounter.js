async function getaccesscounter() {
  const resp = await fetch('/~aneesh/cgi-bin/getaccesscounter.sh');
  const text = await resp.text();
  return Number.parseInt(text);
}
