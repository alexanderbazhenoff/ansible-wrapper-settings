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

If at least one of the pipeline parameters specified in the configuration file does not match the current pipeline
parameters, then all parameters will be resynchronized with the parameters in the configuration file. The checking is
made by parameter names only; type, default values, and other parameter keys are ignored.

The Pipeline may not have required parameters (key [required](#required)), and all parameters can be placed in
[optional](#optional) key (see [Example 4](#example-4)), or not to have any parameters at all: in this case, only the
empty 'parameters' key should be specified. Any required parameter can also become optional without moving it to the
appropriate dictionary [`optional`](#optional) by specifying additional key options [`on_empty`](#required) (see
[Example 2](#example-2)).

### required

The [required](#required) key is located inside the [parameters](#parameters-key) key and consists of a list of
pipeline parameters, each of which has the following keys:

- **name** `[string]` *(mandatory)* - pipeline parameter name.
- **type** `[string]` *(mandatory)* - a parameter type that fully corresponds to the standard parameter types for
  a pipeline. Can be `string` (string), `text` (multiline), `password` (password), `choice` (selection), `boolean`
  (logical). Specifying the type of the pipeline parameter is mandatory, although in some cases it is possible to
  autodetect the type and display the appropriate warning to fix.
- **description** `[string]` *(mandatory)* - description of the pipeline parameter, similar to what is set in the
  pipeline settings graphical interface.
- **default** [depends on `type`] *(optional and compatible with a choice parameter type)* - default value of the
  pipeline parameter. If the default value and the pipeline parameter are not specified, then when running pipeline
  the parameter value will be equivalent to `False` for *boolean* and an empty field for string (including *password*)
  parameters.
- **choices** `[list]` *(compatible with and required for a choice parameter type only)* - possible selection options
  for choice parameters.
- **trim** `[boolean]` *(optional and compatible with a string parameter type only)* - remove leading and trailing
  spaces in the parameter string value. Default is `False`.
- **on_empty** `[dict]` *(optional)* - options for specifying actions if the parameter when starting the pipeline is not
   specified (or empty) (see [Example 2](#example-2)). Contains the following nested keys:

    - **assign** `[string]` *(optional)* - the name of the pipeline parameter which value will be assigned when
      parameter is not specified (empty). It is also possible to assign environment variables, and therefore Jenkins or
      Teamcity variables: `$NODE_NAME`, `$JOB_NAME`, etc. (see [Variable substitution](#variable-substitution)).
    - **fail** `[logical]` *(optional, not compatible with the `warn` key)* - a switch to terminate the pipeline with an
      error if the pipeline parameter is not specified. If the pipeline parameter is required and nested in
      [required](#required), then there is no need to specify `fail: True`.
    - **warn** `[boolean]` *(optional, not compatible with the `fail` key)* - a switch to display a warning, but
      continue pipeline execution if the parameter is not specified.

  If the pipeline parameter is inside [required](#required) and the `on_empty` key is not specified, then an empty
  value for such a parameter will terminate the pipeline with an error.
- **regex** `[string, or list]` *(optional)* - a regular expression, or a list of regular expression strings that will
  be combined into a single string to check the pipeline parameter: if the parameter value does not match the regular
  expression, the current pipeline run will stop with an error.
- **regex_replace** `[dictionary]` *(optional)* - options to control the replacement of pipeline parameter values that
  will be performed when substituting or setting pipeline parameter values. Available only for string (except
  *password*) parameters. Contains the following nested keys:

    - **regex** `[string]` *(required)* - regular expression to search for when replacing the contents of a pipeline
      parameter.
    - *(optional)* - replace matches with the content specified in this key (see [Example 3](#example-3)). If the value
      or `to` key is not specified, then all regular expressions matches specified in the `regex` key will be removed.

  Replacement of pipeline parameter values (with the `regex_replace` key data) is performing at the very beginning of
  the pipeline launch: after possible substitution of other pipeline parameter values (`on_empty` key data) and checking
  these values for `regex` match. Thus, `regex` specifies conditions for checking the original values after possible
  substitution, and `regex_replace` specifies parameters for changing their values of pipeline parameters for usage in
  [pipeline stages](#key-stages) (see [Example 3] (#example-3)).

#### Example 2

```yaml
# Pipeline contains three parameters in the `required` key, but only the `LOGIN` parameter is required, omitting which
# (an empty parameter value) will cause the pipeline to fail. If the `PASSWORD` parameter is not specified, then only
# a warning will appear in the console then the pipeline will continue executing, but if `LOGIN_2` is not specified,
# then only a warning will be issued, then the value will be taken from the pipeline's `LOGIN` parameter.

parameters:
  required:
    - name: LOGIN
      type: string
    - name: LOGIN_2
      type: string
      on_empty:
        assign: $LOGIN
        warn: True
    - name: PASSWORD
      type: password
      on_empty:
        warn: True
```

#### Example 3

```yaml
# A fragment of the configuration file with the required pipline parameter `IP_ADDRESSES`, where spaces will be replaced
# With 'line feed' for substitution inside ansible inventory (not included in example, but means). Also pay attention to
# the syntax in the value of the 'to' field in the regex_replace key of `IP_ADDRESSES` parameter. If pipeline stages use
# this variable, its value will also be formatted: IPs (or hosts) will be separated by line breaks rather than by
# spaces.

parameters:
  required:
    - name: IP_ADDRESSES
      type: string
      description: Space separated IP or DNS list of the host(s).
      regex_replace:
        regex: ' '
        to: "\\\n"
```

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

# Variable substitution

#### Example 21

#### Example 22

# Using variables in scripts and playbooks

#### Example 23

#### Example 24

# Usage examples

# URLs