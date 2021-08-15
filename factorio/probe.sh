if (($(echo | lsof -i -P -n | grep $1 | wc -c) > 0)); then
  echo 'Running on $1';
  exit;
fi;

echo 'Dead';
exit 1;