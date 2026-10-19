# Local MinIO build

The original Docker Hub and Quay images could not be pulled on 2026-10-15.
The runtime image was built from the original project's MinIO release source.

- Official repository: https://github.com/minio/minio
- Release: RELEASE.2024-05-28T17-19-04Z
- Source archive: https://codeload.github.com/minio/minio/tar.gz/refs/tags/RELEASE.2024-05-28T17-19-04Z
- Downloaded archive SHA256: `987c59f79100a8f7e30362c3acd4d8601fddbfc93558e4b05c3b6ad78a8e3ef0`
- Local image: `mewhelp-minio:RELEASE.2024-05-28T17-19-04Z`
- Build command: `docker compose build minio`

The source archive and Dockerfile are kept here so the image can be rebuilt.
The Compose override is loaded automatically; the original Compose file is unchanged.
The source license is included in the image at `/licenses/minio-LICENSE`.
