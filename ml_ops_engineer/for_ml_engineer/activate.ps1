Get-Content .env | foreach {
  $name, $value = $_.split('=')
  if ([string]::IsNullOrWhiteSpace($name) -or $name.Contains('#')) {
    continue
  }
  Set-Content env:\$name $value
}
docker build  -t ml_environment -f ./ml_environment.dockerfile .  --build-arg AWS_ACCESS_KEY_ID=$env:AWS_ACCESS_KEY_ID --build-arg AWS_SECRET_ACCESS_KEY=$env:AWS_SECRET_ACCESS_KEY
docker run --rm -it -p 8888:8888/tcp ml_environment