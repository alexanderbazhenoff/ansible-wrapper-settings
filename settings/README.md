Various examples and configurations for 
[Universal Wrapper Pipeline](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline) (UWP):

- [`example-pipeline.yaml`](example-pipeline.yaml): example of UWP settings with maximum number of possible features and
  parameters.
- [`downstream-example-pipeline.yaml`](downstream-example-pipeline.yaml): example of a UWP downstream pipeline which
  runs from `example-pipeline.yaml`.
- [`install-postgresql.yaml`](install-postgresql.yaml) - example of WUP settings to install and configure 
  PostgreSQL on Linux, a wrapper of
  [postgresql ansible role](https://github.com/alexanderbazhenoff/ansible-collection-linux/tree/main/roles/postgresql). 