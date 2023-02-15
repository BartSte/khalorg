calendar=$1
org=$2
start=today
end=90d

chmod +w $org

khal list \
    --format \
$'* {title} {cancelled} 
  <{start-date} {start-time}-{end-time}>
  :PROPERTIES:
  :ID: {uid}
  :CALENDAR: {calendar}
  :LOCATION: {location}
  :Organizer: {organizer}
  :URL: {url}
  :END:
  {description}'\
    --day-format "" \
    --include-calendar $calendar \
    $start $end > $org

echo "Converted the Khal agenda \"$calendar\" into $org"
chmod -w $org