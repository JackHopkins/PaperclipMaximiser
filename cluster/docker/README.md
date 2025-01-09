# Build

```
docker build -t factorio .
```

```
docker run -d \
  -p 34197:34197/udp \
  -p 27015:27015/tcp \
  factorio
```
