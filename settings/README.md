# Universal Pipeline Wrapper Settings

Various examples and configurations for
[Universal Wrapper Pipeline](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline) (UWP):

- [`example-pipeline.yaml`](example-pipeline.yaml): an abstract, but working example of UWP settings with maximum number
  of possible features and parameters. Some actions of this example pipeline will fail, but it's ok to show how to
  handle and log them.
- [`downstream-example-pipeline.yaml`](downstream-example-pipeline.yaml): an abstract, but working example of a UWP
  which runs from `example-pipeline.yaml` to show how to configure running a downstream pipeline and work with pipeline
  artifacts.
- [`install-postgresql.yaml`](install-postgresql.yaml) - example of pipeline wrapper to install PostgreSQL on Linux,
  a wrapper of
  [postgresql](https://github.com/alexanderbazhenoff/ansible-collection-linux/tree/main/roles/postgresql) ansible role.
