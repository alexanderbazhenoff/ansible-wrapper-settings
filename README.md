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
  the parameter value will be equivalent to `false` for *boolean* and an empty field for string (including *password*)
  parameters.
- **choices** `[list]` *(compatible with and required for a choice parameter type only)* - possible selection options
  for choice parameters.
- **trim** `[boolean]` *(optional and compatible with a string parameter type only)* - remove leading and trailing
  spaces in the parameter string value. Default is `false`.
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
# Pipeline contains three parameters in the `required` key, but only the `LOGIN` parameter is
# required, omitting which (an empty parameter value) will cause the pipeline to fail. If the
# `PASSWORD` parameter is not specified, then only a warning will appear in the console then the
# pipeline will continue executing, but if `LOGIN_2` is not specified, then only a warning will
# be issued, then the value will be taken from the pipeline's `LOGIN` parameter.

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
# A fragment of the configuration file with the required pipline parameter `IP_ADDRESSES`,
# where spaces will be replaced with 'line feed' for substitution inside ansible inventory
# (not included in example, but means). Also pay attention to the syntax in the value of the 'to'
# field in the regex_replace key of `IP_ADDRESSES` parameter. If pipeline stages use this variable,
# its value will also be formatted: IPs (or hosts) will be separated by line breaks rather than by
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

The [optional](#optional) key is located inside the [parameters](#parameters-key) key and consists of a list of optional
pipeline parameters. The structure and list of keys is similar to the [required](#required) key, except that there is no
need to set `on_empty` key values here, since they will be ignored. Thus, only optional pipeline parameters are set in
this key. There is no way to control the pipeline behavior if these parameters are empty.

#### Example 4

```yaml
# A fragment of the pipeline configuration file containing only optional parameters `ONE` and `TWO`.

parameters:
  optional:
    - name: ONE
      type: string
      description: Description of parameter ONE which type is string and default value is 'something'.
      default: something
    - name: TWO
      type: choice
      description: |
        Description of parameter TWO which type is choices.
        TWO parameter includes three choices ('one', 'two' and 'three')
      choices:
        - one
        - two
        - three 
```

## 'stages' key

The key contains a list of pipeline stages, each element of which has the following keys:

- **name** `[string]` *(mandatory)* - name of the pipeline stage. [Variable substitution](#variable-substitution) is
  possible as a key value (see [Example 22](#example-22)).
- **parallel** `[logical]` *(optional)* - a switch, the setting of which leads to parallel launch the list of actions
  (the `actions` key) at the current stage (see [Example 6](#example-6)). Default is `false`.
- **actions** `[list]` *(mandatory)* - list of actions in current stage, each element of which has keys:

  - **before_message** `[string]` *(optional)* - message string before starting the action (see the next `action` key).
    [Variable substitution](#variable-substitution) is possible.
  - **action** `[string]` *(required)* - name of the action, which is specified in the [actions](#actions-key) key in
    the pipeline settings file (see [actions key](#actions-key)). Substitution of the value from the pipeline parameter
    is allowed (see [Example 7](#example-7)). [Variable substitution](#variable-substitution) is possible.
  - **after_message** `[line]` *(optional)* - the message string, which will be displayed after action completion
    regardless of the execution result (see [Example 5](#example-5)). [Variable substitution](#variable-substitution) is
    possible.
  - **ignore_fail** `[boolean]` *(optional)* - a switch to ignore unsuccessful execution of the current action: if set,
    the result of the current action will always be successful. Default is `false`.
  - **stop_on_fail** `[boolean]` *(optional)* - a switch to stop pipeline execution when the action fails: if set, then
    the entire pipeline will be completed immediately after the action fails. Default is `false`.
  - **success_only** `[boolean]` *(optional, not compatible with the `fail_only` key)* - a switch to perform the current
    action only if all previous actions were completed successfully, i.e. the action will be executed if the general
    status of the current pipeline launch is not equal to 'FAILURE' (see [Example 6](#example-6)). Default is `false`.
  - **fail_only** `[boolean]` *(optional, not compatible with the `success_only` key)* - flag to perform the current
    action only if at least one of the previous actions was unsuccessful and the `ignore_fail` key was not set, i.e.
    this is the opposite of `success_only` switch and the action will be performed if the overall status of the current
    pipeline run is 'FAILURE'. Default is `false`.
  - **dir** `[string]` *(optional)* - the name of the directory in which the action will be performed. If there is no
    such directory, then it will be created inside the directory in which the pipeline started (for example, inside
    `workspace` for Jenkins). It is allowed to specify any other full paths, for example: `/tmp` (see
    [Example 6](#example-6)). [Variable substitution](#variable-substitution) is possible.
  - **build_name** `[string]` *(optional)* - the name of the current build, which will be set before starting the
    current action (see [Example 7](#example-7)). If the `success_only` or `fail_only` flags indicate skipping this
    action, then the name of the current build (or current pipeline run) will not be changed.
    [Variable substitution](#variable-substitution) is possible.
  - **node** `[string or dictionary]` *(optional)* - key that determines the node change (for example, Jenkins or
    Teamcity nodes). It can be specified as a string with the possibility of
    [variable substitution](#variable-substitution) and then this value will be the name of the node, or otherwise it is
    specified as a dictionary and can include the following keys:

    - **name** `[string]` *(required, but not compatible with the `label` key)* - node name.
      [Variable substitution](#variable-substitution) is possible.
    - **label** `[string]` *(required, but not compatible with the `name` key)* - node tag (or *node label*).
      [Variable substitution](#variable-substitution) is possible.
    - **pattern** `[boolean]` *(optional)* - if the switch is enabled (`true`), then the search for node will be
      performed by the string in the key `name`, or `label` and will be launched on the first one that matches search
      pattern (see [Example 8](#example-8)). If the switch is disabled, the node will be selected only if there is a
      complete match of the name (in the `name` key), or the node label (in the `label` key).

    To launch an action on any free node, you should specify an empty key `node`, or `node: null` (see
    [example 6](#example-6)).

#### Example 5

```yaml
# A fragment of the configuration file setting up `stage_1` with customized messages.

stages:
  - name: stage_1
    actions:
      - before_message: Starting 'action_name_1'...
        action: action_name_1
        after_message: Just finished 'action_name_1' execution.
      - before_message: Then starting 'action_name_2'...
        action: action_name_2
        fail_message: A custom message for 'action_name_2' that means it was failed.
        success_message: |
          A custom message for 'action_name_2' that means it was complete without errors.
```

#### Example 6

```yaml
# A fragment of a configuration file setting up the stage `stage_name` with parallel action run.
# `action_name_2` will be launched on any free node, while the other actions will be launched
# on the same node where it was originally pipeline was started. `action_name_3` will be executed
# only if the previous two actions have been finished successfully. On executing `action_name_1`
# inside the current folder where the pipeline started (for example, for Jenkins this folder
# called `workspace`) the folder `temp` will be created, while the execution of `action_name_2`
# will be executed in system temporary folder `/tmp`.

  - name: stage_name
    parallel: true
    actions:
      - action: action_name_1
        dir: temp
      - action: action_name_2
        dir: /tmp
        node:
      - action: action_name_3
        success_only: true
```

#### Example 7

```yaml
# A fragment of a configuration file with the pipeline parameter `PIPELINE_ACTION`,
# which specifies the name of the action in `stage_name`. Before the action is executed,
# the current build (or pipeline run) will be named as the `PIPELINE_ACTION` parameter
# defined.

parameters:
  required:
    - name: PIPELINE_ACTION
      type: choice
      description: Action to perform.
      choices:
        - action_one
        - action_two
stages:
  - name: stage_name
    actions:
      - action: $PIPELINE_ACTION
        build_name: $PIPELINE_ACTION
```

#### Example 8

```yaml
# A fragment of the configuration file setting up a `build_stage` with the choice of node
# (displayed as a message to the console before the start of the action - `before_message`).

stages:
  - name: build_stage
    actions:
      - before_message: Starting build on 'build-x64-node-01.domain.com' jenkins node...
        action: build_action
        node: build-x64-node-01.domain.com
      - before_message: Starting build on any jenkins node name starts with 'build-x64-node-'...
        action: build_action
        node:
          name: build-x64-node-
          pattern: true
      - before_message: Starting build on any jenkins node with label 'build_nodes'...
        action: build_action
        node:
          label: build_nodes
      - before_message: Starting build on any jenkins node with label contains '_nodes'...
        action: build_action
        node:
          label: _nodes
```

## 'actions' key

The key is a dictionary and defines named actions, where each nested key is the name of the action, and its values are
the action parameters:

```yaml
actions:
  action_name_1:
    action_parameter_1: value_1
    action_parameter_2: value_2
```

The action type is determined by the key parameters specified in it. The following types of actions are supported:

- [**source cloning (git)**](#action-clone-sources-with-git),
- [**install ansible collection from Ansible Galaxy**](#action-install-ansible-collection-from-ansible-galaxy),
- [**run ansible playbook**](#action-run-ansible-playbook),
- [**run script**](#action-run-script),
- [**get artifact files**](#action-get-artifact-files),
- [**get files from node (stash)**](#action-get-files-from-node-stash),
- [**transfer files to node (unstash)**](#action-transfer-files-to-node-unstash),
- [**run downstream pipeline**](#action-run-downstream-pipeline),
- [**notifications send**](#action-notifications-send) ([email](#sending-notifications-via-email), or
  [mattermost](#sending-notifications-via-mattermost)).

[Variable substitution](#variable-substitution) is possible in any string values of the action parameters.

If any action was specified in the `actions` key, but wasn't specified in the `stages` key (or its action name wasn't
passed during variable substitution), this action will be ignored. Also, if the `action` field in an action list
element in `stages` contains an empty value at the moment of checking the syntax and pipeline configuration parameters
(for example, the variable will be specified later in one of the stage's scripts, so a link from `stages` to `actions`
has not been set yet - see [Example 18](#example-18)), then checking the syntax and parameters of this action won't be
performed.

### Action: clone sources with git

- **repo_url** `[string]` *(required)* - link to the GitLab/GitHub repository.
- **repo_branch** `[string]` *(optional)* - name of the branch in the repository. If the key is missing, then `main`
  branch.
- **credentials** `[string]` *(optional)* - CredentialsID for accessing the repository (see [Example 9](#example-9)).
If the key is missing, then the value is taken from the `GitCredentialsID` constant in the library
["jenkins-shared-library"](https://github.com/alexanderbazhenoff/jenkins-shared-library/blob/main/src/org/alx/commonFunctions.groovy).
- **directory** `[string]` *(optional)* - directory inside the workspace for cloning. If the key is missing, project
cloning will be done into the workspace.

[Variable substitution](#variable-substitution) is possible in all keys of this action.

#### Example 9

```yaml
# A fragment of the configuration file setting the action with defined CredentialsID to clone
# sources from GitLab via ssh into the `subdirectory_name` folder located in the workspace,
# and switching to the `develop` branch.

actions:
  git_clone_action_name:
    repo_url: ssh://git@gitlab.com:username/project-name.git
    repo_branch: develop
    directory: subdirectory_name
    credentials: a123b01c-456d-7890-ef01-2a34567890b1
```

### Action: install ansible collection from Ansible Galaxy

#### Example 10

### Action: run ansible playbook

#### Example 11

### Action: run script

#### Example 12

### Action: get artifact files

#### Example 13

### Action: get files from node (stash)

### Action: transfer files to node (unstash)

#### Example 14

### Action: run downstream pipeline

#### Example 15

### Action: notifications send

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