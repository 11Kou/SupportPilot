FROM golang:1.22.12-bookworm AS builder
WORKDIR /src
ADD source.tar.gz /src/
WORKDIR /src/minio-RELEASE.2024-05-28T17-19-04Z
ENV CGO_ENABLED=0 GOTOOLCHAIN=local
RUN go build -p 2 -trimpath -ldflags="-s -w" -o /minio .

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl
COPY --from=builder /minio /usr/local/bin/minio
COPY --from=builder /src/minio-RELEASE.2024-05-28T17-19-04Z/LICENSE /licenses/minio-LICENSE
ENTRYPOINT ["/usr/local/bin/minio"]
