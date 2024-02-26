<!-- markdownlint-disable MD001 MD007 MD025 MD033 MD041 -->
<div align='center'>

# [Universal Wrapper Pipeline](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline) format description

[![Super-Linter](https://github.com/alexanderbazhenoff/universal-wrapper-pipeline-settings/actions/workflows/super-linter.yml/badge.svg?branch=main)](https://github.com/marketplace/actions/super-linter)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)
[![GitHub License](https://img.shields.io/github/license/alexanderbazhenoff/jenkins-universal-wrapper-pipeline)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)
[![Tweet](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://twitter.com/intent/tweet?text=Create+your+pipelines+easier+and+faster%21%20&url=https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline&hashtags=devops,cicd,jenkins,ansible,yaml)

<span style="font-size:0.8em;">[**English**](README.md) • [Russian](README_RUS.md)</span>
</div>

The Universal Wrapper Pipeline configuration file should be corresponded to all
[yaml syntax standards](https://yaml.org/). One single settings file for one single wrapper pipeline. But exceptions
using [regular expressions](#example-1) in pipeline names are also possible: one configuration file can be used in
several copies of pipeline with different names. The general structure of configuration files is described in section
['Configuration files main keys'](#configuration-files-main-keys).

## Configuration files names

Configuration files should be named as `pipeline-name.yaml` and placed in `settings/` folder of repository (can be
changed by `SettingsRelativePathPrefix` pipeline constant or `JUWP_RELATIVE_PATH_PREFIX` environment variable).
Prefixes and postfixes are allowed in the pipeline name, to remove them and bring configuration file names to uniformity
there is a `PipelineNameRegexReplace` pipeline constant (or `JUWP_PIPELINE_NAME_REGEX_REPLACE` environment variable).

#### Example 1

Pipeline constant looks like:

```groovy
final List PipelineNameRegexReplace = ['^(admin|devops|qa)_']
```

So pipelines with `admin_example-pipeline`, `devops_example-pipeline` and `qa_example-pipeline` names run the only one
`example-pipeline.yaml` configuration file.

*Regular expressions and setting the path inside the repository are intended to simplify structuring configuration files
inside the repository and customization on different needs. You may leave a path by default and regular expressions as
empty, then configuration files should be placed as: `settings/admin_example-pipeline.yaml`,
`settings/devops_example-pipeline.yaml` and `settings/qa_example-pipeline.yaml`.

# Configuration files main keys

The configuration file consists of several keys, each of which divides it into several “sections”:

```yaml
---

parameters:
  # Keys in parameters dict...
stages:
  # Keys in stages dict...
actions:
  # Keys in actions dict...
scripts:
  # Keys in scripts dict...
playbooks:
  # Keys in playbooks dict...
inventories:
  # Keys in inventories dict...
```

- [**parameters**](#parameters-key) `[dict]` *(required for parametrized pipelines)* - pipeline parameters, those that
  you set in GUI before a pipeline run.
- [**stages**](#stages-key) `[list]` *(mandatory)* - list of pipeline stages.
- [**actions**](#actions-key) `[dict]` *(mandatory)* - action defining that can also refer to a playbook and inventory
  inside [playbooks](#playbooks-key) and ['inventories'](#inventories-key) keys, or to a script from
  ['scripts'](#scripts-key).
- [**scripts**](#scripts-key) `[dict]` *(optional)* - a key containing scripts that will be launched when the
  corresponding action is executed.
- [**playbooks**](#playbooks-key) `[dict]` *(optional)* - a key containing ansible playbooks that will be launched
  when the corresponding action is executed.
- [**inventories**](#inventories-key) `[dict]` *(optional)* - a key containing ansible inventories that will be used
  together with playbooks of the same name when executing the action. If there is at least one playbook in the
  [playbooks](#playbooks-key) key, the presence of ['inventories'](#inventories-key) key and at least one inventory with
  the name `default` are required.

## 'parameters' key

The key contains pipeline parameters, presented as a dictionary, which are divided into three types:

- [**required**](#required) `[list]` - mandatory pipeline parameters, without setting the values of which the current
   pipeline run will end with an error. They are described inside the key of the same name [required](#required), nested
   in the key [parameters](#parameters-key):

  ```yaml
  parameters:
    required:
  ```

- [**optional**](#optional) `[list]` - optional; their empty values will neither warnings results nor cause the
  pipeline to stop with an error. Similar as 'required' these parameters are described in the key with corresponding
  name nested in the 'parameters' key.
- [**built-in**](#built-in-pipeline-parameters) - 'built-in' pipeline parameters: `SETTINGS_GIT_BRANCH`, `NODE_NAME`,
  `NODE_TAG`, `UPDATE_PARAMETERS`, `DRY_RUN` and `DEBUG_MODE`. These parameters are already built directly into the
   pipeline code (inside the `BuiltinPipelineParameters` constant). There is no need to set them in the configuration
   file, but they can be used in pipeline configuration file to assign their values to other pipeline variables (see
   `assign` in [Example 2](#example-2)), or use in playbooks and scripts.

### required

#### Example 2

#### Example 3

### optional

#### Example 4

## 'stages' key

#### Example 5

#### Example 6

#### Example 7

#### Example 8

## 'actions' key

### Action: clone sources with git

#### Example 9

### Action: install ansible collection from Ansible Galaxy

#### Example 10

### Action: run ansible playbook

#### Example 11

### Action: run script

#### Example 12

### Action: getting artifact files

#### Example 13

### Action: get files from node (stash)

### Action: put files on node (unstash)

#### Example 14

### Action: run downstream pipeline

#### Example 15

### Action sending notifications

#### Sending notifications via email

#### Example 16

#### Sending notifications via mattermost

#### Example 17

## 'scripts' key

#### Example 18

## 'playbooks' key

## 'inventories' key

#### Example 19

#### Example 20

# Built-in pipeline parameters

# Built-in pipeline variables