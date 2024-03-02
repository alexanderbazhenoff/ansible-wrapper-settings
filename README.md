<!-- markdownlint-disable MD001 MD007 MD025 MD033 MD041 -->
<div align='center'>

# [Universal Wrapper Pipeline](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline) format description

[![Super-Linter](https://github.com/alexanderbazhenoff/universal-wrapper-pipeline-settings/actions/workflows/super-linter.yml/badge.svg?branch=main)](https://github.com/marketplace/actions/super-linter)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)
[![GitHub License](https://img.shields.io/github/license/alexanderbazhenoff/universal-wrapper-pipeline-settings)](LICENSE)
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
    - **fail** `[boolean]` *(optional, not compatible with the `warn` key)* - a switch to terminate the pipeline with an
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

    - **regex** `[string]` *(mandatory)* - regular expression to search for when replacing the contents of a pipeline
      parameter.
    - *(optional)* - replace matches with the content specified in this key (see [Example 3](#example-3)). If the value
      or `to` key is not specified, then all regular expressions matches specified in the `regex` key will be removed.

  Replacement of pipeline parameter values (with the `regex_replace` key data) is performing at the very beginning of
  the pipeline launch: after possible substitution of other pipeline parameter values (`on_empty` key data) and checking
  these values for `regex` match. Thus, `regex` specifies conditions for checking the original values after possible
  substitution, and `regex_replace` specifies parameters for changing their values of pipeline parameters for usage in
  [pipeline stages](#stages-key) (see [Example 3] (#example-3)).

#### Example 2

```yaml
# This Pipeline contains three parameters in the `required` key, but only the `LOGIN` parameter
# is required, omitting which (an empty parameter value) will cause the pipeline to fail. If the
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
# A part of the configuration file with the required pipline parameter `IP_ADDRESSES`,
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
# A part of the pipeline configuration file containing only optional parameters `ONE` and `TWO`.

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
- **parallel** `[boolean]` *(optional)* - a switch, the setting of which leads to parallel launch the list of actions
  (the `actions` key) at the current stage (see [Example 6](#example-6)). Default is `false`.
- **actions** `[list]` *(mandatory)* - list of actions in current stage, each element of which has keys:

  - **before_message** `[string]` *(optional)* - message string before starting the action (see the next `action` key).
    [Variable substitution](#variable-substitution) is possible.
  - **action** `[string]` *(mandatory)* - name of the action, which is specified in the [actions](#actions-key) key in
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
# A part of the configuration file setting up `stage_1` with customized messages.

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
# A part of a configuration file setting up the stage `stage_name` with parallel action run.
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
# A part of a configuration file with the pipeline parameter `PIPELINE_ACTION`,
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
# A part of the configuration file setting up a `build_stage` with the choice of node
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

- **repo_url** `[string]` *(mandatory)* - link to the GitLab/GitHub repository.
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
# A part of the configuration file setting the action with defined CredentialsID to clone
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

- **collection** `[string, or list]` *(mandatory)* - namespace and name of the collection from
  [Ansible Galaxy](https://galaxy.ansible.com/) for installation (see [Example 10](#example-10)), or a list of them.

The collection is always installing forcibly (using parameter `force`), which ensures their constant updating.
[Variable substitution](#variable-substitution) is possible in all collection names.

#### Example 10

```yaml
# An example of configuration file with an action installing one Ansible collection
# `namespace.collection_name` and collections list.

actions:
  ansible_galaxy_install_action_name:
    collections: namespace.collection_name
  ansible_galaxy_install_list_action_name:
    collections:
      - namespace_1.collection_name_1
      - namespace_2.collection_name_2
```

### Action: run ansible playbook

- **playbook** `[string]` *(mandatory)* - playbook name (see [Example 11](#example-11) and [playbooks](#playbooks-key)
  key). [Variable substitution](#variable-substitution) is possible.
- **inventory** `[string]` *(optional)* - inventory name (see the [inventories](#inventories-key) key). If this key is
  missing, then `default` ansible inventory inside the [inventories](#inventories-key) key is searched.

All environment variables (and pipeline parameters), as well as
[Built-in pipeline variables](#built-in-pipeline-variables) will be available during playbook run. For example,
to get the value of `universalPipelineWrapperBuiltIns.myCustomReport` inside a playbook, just specify its key as an
environment variable: `$myCustomReport`.

#### Example 11

```yaml
# A part of the configuration file with launching playbook as an action and
# `ping_playbook_name` itself.

actions:
  ping_action_name:
    playbook: ping_playbook_name

playbooks:
  ping_playbook_name: |
    - hosts: all
      tasks:
        - name: Ping
          ansible.builtin.ping:
```

### Action: run script

- **script** `[line]` *(mandatory)* - the name of the script to run it as a separate script ([Example 12](#example-12)),
  or run as part of this pipeline (see the [scripts](#scripts-key) key).
  [Variable substitution](#variable-substitution) is possible.

#### Example 12

```yaml
# A part of the configuration file with running the script as an action
# and the `bash_script_name` itself.

actions:
  run_script_action_name:
    script: bash_script_name

scripts:
  bash_script_name:
    script: |
      #!/usr/bin/env bash
      printf "This is a %s script.\n" "$(cut -d'/' -f4 <<<"$SHELL")"
```

In a running script, same as a [playbooks](#action-run-ansible-playbook), environment variables and variables built into
the pipeline are also available. When [running a script "as part of a pipeline"](#scripts-key) it is also possible to
change key values of [built-in pipeline variables](#built-in-pipeline-variables) `universalPipelineWrapperBuiltIns`:
all its changes will be inherited by other stages and actions of the pipeline. While changes to environment variables
inside scripts will not be inherited by other stages and actions of the pipeline. To save values as a result of the
script, use built-in pipeline variables, or save the result to a file.

All scripts (except [of “as part of the pipeline”](#scripts-key)) are running through a shell call. To select the
appropriate environment, you should specify an appropriate hashbang.

### Action: get artifact files

- **artifacts** `[string]` *(mandatory)* - path and name mask (or a comma-separated list of them) for
  [archiving artifact files](https://www.jenkins.io/doc/pipeline/tour/tests-and-artifacts/).
  [Variable substitution](#variable-substitution) is possible.
- **excludes** `[string]` *(optional)* - path and name mask (or a comma-separated list of them) to exclude from
  archiving (see [Example 13](#example-13)). [Variable substitution](#variable-substitution) is possible.
- **allow_empty** `[boolean]` *(optional)* - flag that allows the absence of files that meet the conditions, specified
  in `artifacts` and `excludes`. By default, `false`, that means that absence of files that satisfy conditions will
  cause an error.
- **fingerprint** `[boolean]` *(optional)* - a switch to include a
  [checksum for artifact files](https://www.jenkins.io/doc/book/using/fingerprints/). Default is `false`.

#### Example 13

```yaml
# A part of the configuration file setting up the action to get regression testing logs,
# unit tests and general results (except unit test logs in JSON format). Missing files are
# allowed, checksum calculation is disabled.

actions:
  archive_artifacts_action_name:
    artifacts: regression_tests/**/logs/*, unit_tests/**/logs/*, results.txt
    excludes: unit_tests/**/logs/*.json
    allow_empty: true
    fingerprint: false
```

### Action: get files from node (stash)

- **stash** `[string]` *(mandatory)* - the name of the files set to get files from node (for example,
[stash in Jenkins](https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/#stash-stash-some-files-to-be-used-later-in-the-build)).
  In fact, this is an identifier for a file set. [Variable substitution](#variable-substitution) is possible.
- **includes** `[string]` *(optional)* - path and name mask (or a comma-separated list of them) for building files with
  node. [Variable substitution](#variable-substitution) is possible.
- **excludes** `[string]` *(optional)* - path and name mask (or a comma-separated list of them) to exclude files from
  obtaining (see [Example 14](#example-14)). [Variable substitution](#variable-substitution) is possible.
- **default_excludes** `[boolean]` *(optional)* - a switch to enable default exceptions (for example, for Jenkins, Ant
  exceptions will have [the following list](https://ant.apache.org/manual/dirtasks.html#defaultexcludes)). Default is
  `true`.
- **allow_empty** `[boolean]` *(optional)* - a switch that allows the absence of files that meet the conditions,
  specified in `artifacts` and `excludes`. The default is `false`, when the absence of files that satisfy the conditions
  in `includes`, `excludes` and `default_excludes` will cause an error.

### Action: transfer files to node (unstash)

- **unstash** `[string]` *(required)* - name of a set of files for building files with node (for example,
[stash in Jenkins](https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/#stash-stash-some-files-to-be-used-later-in-the-build)).
  In fact this is an identifier for a file set. [Variable substitution](#variable-substitution) is possible. To set the
  path to transfer the files in, use [action key](#stages-key) `dir` (see [Example 14](#example-14)).

#### Example 14

```yaml
# A part of the configuration file setting up the stage and actions of to move files
# between nodes: all files except files in json format are copied from the logs folder in
# the workspace on node 'my_node' to the 'my_folder' folder in the workspace on node
# 'another_node'. The absence of files specified in the `includes` condition is allowed,
# since `allow_empty` is set.

stages:
  - name: stash_unstash
    actions:
      - action: stash_files_from_node_action_name
        node: my_node
      - action: unstash_files_from_node_action_name
        node: another_node
        dir: my_unstash_folder

actions:
  stash_files_from_node_action_name:
    stash: my_stash_name
    includes: logs/*
    excludes: logs/*.json
    allow_empty: true
  unstash_files_from_node_action_name:
    unstash: my_stash_name
```

### Action: run downstream pipeline

An action that specifies a downstream pipeline run, or a job (hereinafter 'pipeline'), getting results and artifact
files for the current pipeline run.

- **pipeline** `[string]` *(mandatory)* - the name of downstream pipeline.
  [Variable substitution](#variable-substitution) is possible.
- **parameters** `[list]` - *(optional)* - list of parameters. If a downstream pipeline is parameterized, then each
  element of the list is a parameter and has the following keys (see [Example 15](#example-15)):

  - **name** `[string]` *(mandatory)* - downstream pipeline parameter name.
  - **type** `[string]` *(mandatory)* - downstream pipeline parameter type: `string`, `text`, `password`, or `boolean`.
  - **value** `[string or boolean]` *(mandatory)* - string or logical value, depending on a downstream parameter type.
    [Variable substitution](#variable-substitution) is possible.

- **propagate** `[boolean]` *(optional)* - pass completion status from the downstream pipeline: if set to `true`, or the
  key is not specified, then failure of a downstream pipeline will bring an error in the upstream pipeline. However, if
  `ignore_fail` is set for the current action in upstream pipeline, then the error will be transmitted, but the pipeline
  will not end with an error and will continue execution - see [stages key](#stages-key)). If `propagate` is not set,
  the completion status of the downstream pipeline will not be passed to the upstream (for Jenkins this is a
  *'Propagate errors'* option). Default is `true`.
- **wait** `[boolean]` *(optional)* - wait for the downstream pipeline to complete: if set, or not specified, then wait.
  Otherwise, the upstream pipeline will not wait, and it will be impossible to receive completion status and artifact
  files from the downstream pipeline. Actually in Jenkins it is 'Wait for completion' option. Default is `true`.
- **copy_artifacts** `[dictionary]` *(optional)* - additional parameters for copying artifact files from a dowstream
  pipeline (see [Example 15](#example-15) and [Copy Artifacts](https://plugins.jenkins.io/copyartifact/) plugin for
  Jenkins):

  - **filter** `[string]` *(mandatory)* - mask of paths and names (or a comma-separated list of them) to get artifact
    files from a downstream pipeline. [Variable substitution](#variable-substitution) is possible.
  - **excludes** `[string]` *(optional)* - a mask of paths and names (or a comma-separated list of them) to exclude
    artifact files from the list. [Variable substitution](#variable-substitution) is possible.
  - **target_directory** `[string]` *(optional)* - path inside the workspace to which artifact files will be copied.
    If the key is not specified, then the artifact files will be copied to the workspace directly.
    [Variable substitution](#variable-substitution) is possible.
  - **optional** `[boolean]` *(optional)* - if `true`, then the upstream pipeline will not fail with an error if there
    are no artifact files that match the conditions in the `filter` and `excludes` keys. Otherwise, if there are no
    artifact files, the pipeline will fail with an error at the running the downstream pipeline action. However, if
    `ignore_fail` is set in the stage definition, then the error will be passed to the upstream pipeline, but the
    pipeline will not end with an error and will continue execution (see [stages key](#stages-key)). Default is `false`.
  - **flatten** `[boolean]` *(optional)* - `true` to ignoring a directory structure of copied artifact files. If the key
    is not specified, or `false`, then the entire directory structure will be preserved. Default is `false`.
  - **fingerprint** `[boolean]` *(optional)* - a switch to enable
    [checksum for artifact files](https://www.jenkins.io/doc/book/using/fingerprints/). Default is `false`.

  Please note that
  [Universal Wrapper Pipeline](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline) copies artifact
  files from the downstream pipelines called by itself. There is no selection “by last successful”, “by last completed”
  and/or by pipeline/job name.

#### Example 15

```yaml
---

# An example of a configuration file defining the only pipeline parameter
# `UPSTREAM_PARAMETER`, the stage `run_downstream_pipeline_stage_name` and the
# action to launch `downstream_pipeline_name` downstream pipeline, to which the
# value of the upstream parameter `UPSTREAM_PARAMETER` is passed. If the execution
# of the downstream pipeline `downstream_pipeline_name` fails, or during its execution
# the logs folder is empty, then this will not cause errors.

parameters:
  required:
    - name: UPSTREAM_PARAMETER
      type: string
      
stages:
  - name: run_downstream_pipeline_stage_name
    actions:
        action: run_jenkins_pipeline_action_name

actions:
  run_jenkins_pipeline_action_name:
    pipeline: downstream_pipeline_name
    parameters:
      - name: UPSTREAM_PARAMETER
        type: string
        value: $UPSTREAM_PARAMETER
    propagate: false
    copy_artifacts:
      filter: logs/*
      fingerprint: true
      target_directory: logs
      optional: true
```

### Action: notifications send

- **report** `[string]` *(required)* - method for sending notifications. [Variable substitution](#variable-substitution)
  is possible. Supported:

  - [**via email**](#sending-notifications-via-email) (see [Example 16](#example-16)) - value is set to `email`,
  - [**via mattermost**](#sending-notifications-via-mattermost) (see [Example 17](#example-17)) - value is set to
    `mattermost`.

The other keys parameters depend on the method of sending notifications.

#### Sending notifications via email

To send email notifications in Jenkins, you will need [Email Extension](https://plugins.jenkins.io/email-ext/).

- **to** `[string]` *(mandatory)* - recipient(s) addresses. [Variable substitution](#variable-substitution) is possible.
- **reply_to** `[string]` *(optional)* - email address to respond to this notification.
  [Variable substitution](#variable-substitution) is possible. Default for Jenkins is `'$DEFAULT_REPLYTO'`.
- **subject** `[string]` *(optional)* - mail subject. [Variable substitution](#variable-substitution) is possible.
- **body** `[string]` *(optional)* - mail text. [Variable substitution](#variable-substitution) is possible.

#### Example 16

```yaml
---

# An example of a configuration file specifying the only pipeline parameter `EMAIL`,
# which set a list of recipients separated by a space (will be replaced by ', '),
# the only stage and action of sending a notification via email. The mail text contains
# built-in Jenkins variables: `env.JOB_NAME` (current pipeline build name),
# `env.BUILD_URL` (URL to the current build), as well as the `multilineReport` (key of
# `universalPipelineWrapperBuiltIns` variable) and `EMAIL` pipeline parameter.

parameters:
  required:
    - name: EMAIL
      type: string
      description: Space separated email recipients list.
      regex_replace:
        regex: ' '
        to: ', '
      
stages:
  - name: email_report_stage_name
    actions:
        action: email_report_action_name

actions:
  email_report_action_name:
    report: email
    to: $EMAIL
    subject: Test email report
    body: |
      Hi,
      
      I've just run a test for universal jenkins wrapper pipeline for '$JOB_NAME' pipeline, finished with
      '$currentBuild_result' state. As you see sending report to $EMAIL done.
      
      Overall report is:
      $multilineReport
      
      Check pipeline console for details: $BUILD_URL/console
      This report was generated automatically, please do not reply.
      
      Sincerely,
      Your Jenkins.
```

#### Sending notifications via Mattermost

- **url** `[string]` *(mandatory)* - URL of Mattermost webhook, containing the channel key. For example:
  `https://mattermost.com/hooks/<token>` (see [Example 17](#example-17)).
  [Variable substitution](#variable-substitution) is possible.
- **text** `[string]` *(mandatory)* - notification text. [Variable substitution](#variable-substitution) is possible.

#### Example 17

```yaml
# A part of the configuration file with the task of sending a notification to
# Mattermost. URL and token are just for example.

actions:
  mattermost_report_action_name:
    report: mattermost
    url: https://mattermost.com/hooks/31895e09lg2m0g44dk4qeb847s
    text: |
      Hi, I've just run a test for universal jenkins wrapper pipeline: $JOB_NAME.
      Overall report is:
      ```
      $multilineReport
      ```
      Please ignore this automatic report.
```

## 'scripts' key

The key contains scripts, where each nested key is the name of that script, and its value is a dictionary with script
parameters and script content. Scripts can also be executed “as part of a pipeline” (see [Example 18](#example-18)).

- **pipeline** `[boolean]` *(optional)* - if this switch specified or set, then the script is executed 'as part of the
  pipeline' (see [Example 18](#example-18)) and then you must also set the key, indicating in which CI tool (or
  environment) this script should be executed: `jenkins`, `teamcity`, etc. If the key is not specified, or `false`, set
  the code inside a `scripts` key that t will be executed 'separately from the pipeline' (although when launched it will
  also inherit all environment variables) (see [Example 18](#example-12)). The difference is that in the first case you
  can run code that native to the CI tool (Groovy for Jenkins, or Kotlin for Teamcity). In the second case you can run a
  script in any language (perhaps you may need to install it on node) that will start as a subprocess from a pipeline.
- **script** `[string]` *(required if not `pipeline: true`)* - script contents. Acceptable use hashbang (see
  [Example 18](#example-12)).
- **jenkins** `[string]` *(optional)* - code to execute only when run in Jenkins "as part of the pipeline". All pipeline
  variables will be inherited (see [Built-in pipeline variables](#built-in-pipeline-variables)).
- **teamcity** `[string]` *(optional)* - code to execute only when run in Teamcity "as part of the pipeline". All
  pipeline variables will be inherited (see [Built-in pipeline variables](#built-in-pipeline-variables)).

#### Example 18

```yaml
# A part of the configuration file with an action to run the code
# 'as part of the pipeline' for Jenkins and Teamcity.

actions:
  run_part_of_pipeline_action_name:
    script: script_name

scripts:
  script_name:
      pipeline: true
      jenkins: |
        println String.format('EMAIL provided for %s action is awesome: %s', env.PIPELINE_ACTION, env.EMAIL)
      teamcity: |
        println(String.format("EMAIL provided for %s action is awesome: %s", env.PIPELINE_ACTION, env.EMAIL))
```

## 'playbooks' key

The key contains ansible playbooks, where each nested key is the name of this script, and its values are the contents of
the playbook (see [Example 19](#example-19)). [Variable substitution](#variable-substitution) is possible.

## 'inventories' key

The key contains an ansible inventory, where each nested key is the name of that inventory, and its value is the
contents of the inventory. [Variable substitution](#variable-substitution) is possible.

For all playbooks, at least one inventory with the name `default` must be specified in the configuration file, which
will be used for all playbooks (see [Example 19](#example-19)) in this configuration file. Each playbook can also have
its own inventory: in this case, the inventory is created with the same name as the playbook to which it corresponds
(see [Example 20](#example-20)). [Variable substitution](#variable-substitution) is possible.

#### Example 19

```yaml
---

# An example of a configuration file with pipeline parameters, stages, actions, playbook
# and default inventory. All pipeline parameters specify hosts credentials for which
# anisble ping will be performed. There is one single inventory named `default`, but in
# this example the inventory could also have the name `run_ansible_playbook_action_name`.

parameters:
  required:
    - name: IP_ADDRESSES
      type: string
      description: |
        Space separated IP or DNS list of the host(s) to asnible ping: try to connect to host, verify a usable python
        and return.
      regex_replace:
        regex: ' '
        to: "\\\n"
    - name: SSH_LOGIN
      type: string
      description: SSH login for all specified hosts.
    - name: SSH_PASSWORD
      type: password
      description: SSH password for all specified hosts.

stages:
  - name: stage_name
    actions:
      - action: run_ansible_playbook_action_name

actions:
  run_ansible_playbook_action_name:
    playbook: playbook_name

playbooks:
  playbook_name: |
    - hosts: all
      tasks:
        - name: Perform ansible ping on the host(s)
          ansible.builtin.ping:

inventories:
  default: |
    [all]
    $IP_ADDRESSES
    [all:vars]
    ansible_connection=ssh
    ansible_become_user=root
    ansible_ssh_common_args='-o StrictHostKeyChecking=no'
    ansible_ssh_user=$SSH_LOGIN
    ansible_ssh_pass=$SSH_PASSWORD
```

#### Example 20

```yaml
# A fragment of a configuration file with two playbooks
# (`ansible_ping_playbook_name` and `install_curl_playbook_name`) and inventory for
# each of them: when executing `ansible_ping_playbook_name`, authentication occurs
# using a password, when executing `install_curl_playbook_name` using an ssh key.

playbooks:
  ansible_ping_playbook_name: |
    - hosts: all
      tasks:
        - name: Perform ansible ping on the host(s)
          ansible.builtin.ping:
  install_curl_playbook_name: |
    - hosts: all
      become: true
      become_method: sudo
      gather_facts: true
      tasks:
        - name: Install curl using ansible.builtin.package ansible module Generic OS package manager
          ansible.builtin.package:
          name: curl
          state: present

inventories:
  ansible_ping_playbook_name: |
    [all]
    $IP_ADDRESSES
    [all:vars]
    ansible_connection=ssh
    ansible_become_user=root
    ansible_ssh_common_args='-o StrictHostKeyChecking=no'
    ansible_ssh_user=$SSH_LOGIN
    ansible_ssh_pass=$SSH_PASSWORD
  install_curl_playbook_name: |
    [all]
    $IP_ADDRESSES

    [all:vars]
    ansible_connection=ssh
    ansible_ssh_common_args='-o StrictHostKeyChecking=no'
    ansible_user=$SSH_LOGIN
    ansible_ssh_private_key_file=~/.ssh/id_rsa
```

# Built-in pipeline parameters

- `SETTINGS_GIT_BRANCH` - branch from which pipeline settings will be loaded.
- `NODE_NAME` - the name of the node on which the
  [Universal Wrapper Pipeline](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline) will be
  launched.
- `NODE_TAG` - node tag (or *node label*).
  [Universal Wrapper Pipeline](https://github.com/alexanderbazhenoff/jenkins-universal-wrapper-pipeline) starts on the
  node to which this tag is assigned.
- `UPDATE_PARAMETERS` - if enabled, then update the pipeline parameters from the configuration file without performing
  stages and actions. Can be used if the pipeline parameters are changed in the configuration file, but anything except
  the name (type, default values, description, or handling).
- `DRY_RUN` - if enabled, no actions and changes will be performed, but service messages will be displayed in the
  console as if the 'dry run' had not been enabled.
- `DEBUG_MODE` - режим отладки для детализированного логирования в консоль.

All [pipeline-built-in parameters](#pipeline-built-in-parameters) are available for use in playbooks, inventory, scripts
and pipelines by the same way as in any other pipelines: for example, the "DRY_RUN" parameter in Jenkins will be
available through the environment variable `DRY_RUN` and the Groovy variables `env.DRY_RUN` and `params_DRY_RUN`.

# Built-in pipeline variables

The built-in `universalPipelineWrapperBuiltIns` variable *[dictionary, or Map]* contains keys that can be used in the
configuration file (for example, when generating reports):

- `universalPipelineWrapperBuiltIns.multilineReportMap` *[dictionary, or Map]* - contains a dictionary of statuses and
  information about each action in the pipeline stages. The key is intended to be used in code "as part of a pipeline".
  The structure of the Map is identical to the description of the `addPipelineStepsAndUrls()` function in
  [jenkins-shared-library](https://github.com/alexanderbazhenoff/jenkins-shared-library) in the function and looks like:

  ```groovy
  universalPipelineWrapperBuiltIns.multilineReport = [
          'stage_1[0]': [
              name : 'stage_1 [0]',
              state: true|false,
              url  : 'Information about 1st action in stage_1.'
          ],
          'stage_1[1]': [
              name : 'stage_1 [1]',
              state: true|false,
              url  : 'Information about 2nd action in stage_1.'
          ],
          'stage_2[0]': [
              name : 'stage_2 [0]',
              state: true|false,
              url  : 'Information about 1st action in stage_2.'
          ]
  ]
  ```

- `universalPipelineWrapperBuiltIns.multilineReportMapStages` *[dictionary, or Map]* - contains only a dictionary of
  stage states. The structure is similar to *multilineReportMap*:

  ```groovy
  universalPipelineWrapperBuiltIns.multilineReportMapStages = [
          'stage_1': [
              name : 'stage_1',
              state: true|false,
              url  : '6 actions.'
          ],
          'stage_2': [
              name : 'stage_2',
              state: true|false,
              url  : '4 actions in parallel.'
          ]
  ]
  ```

- `universalPipelineWrapperBuiltIns.multilineReport` *[string]* - contains a text table of statuses and information
  about each action and stage of the pipeline. The content is identical to *multilineReportMap*, but more printable.
  This key does not contain color codes (ASCII colors), that is more convenient for inserting when generating various
  [notifications](#action-notifications-send).
- `universalPipelineWrapperBuiltIns.multilineReportStages` *[string]* - contains only a text table of stage states. No
  color codes included, because of intended for generating the text of various
  [notifications](#action-notifications-send). The overall stage execution status will be updated only after all actions
  in the stage have been completed.
- `universalPipelineWrapperBuiltIns.multilineReportFailed` *[string]* - contains a text table of only failed actions in
  stages. Contains an empty string when all actions are completed successfully. No color codes included, because of 
  intended for generating the text of various [notifications](#action-notifications-send).
- `universalPipelineWrapperBuiltIns.currentBuild_result` *[string]* - contains overall execution state of the current
  pipeline run: `SUCCESS`, or `FAILED` (for example, for Jenkins its contents are identical to `currentBuild.result`).
- `universalPipelineWrapperBuiltIns.multilineReportStagesFailed` *[string]* - contains a text table of only failed
  stages. Contains an empty string when all stages are completed successfully. No color codes, because of intended for
  generating the text of various [notifications](#action-notifications-send). The overall stage execution updates
  only after all actions in the stage have been completed.
- `universalPipelineWrapperBuiltIns.currentBuild_result` *[string]* - contains an overall execution state of the current
  pipeline run: `SUCCESS`, or `FAILED` (for example, for Jenkins this value is identical to `currentBuild.result`).
- `universalPipelineWrapperBuiltIns.ansibleCurrentInstallationName` *[string]* (deprecated) - contains the name of the
  ansible installation (for example, in Jenkins its value is set in the
  [Global Configuration Tool](https://issues.jenkins.io/browse/JENKINS-67209). Not used and will probably be removed
  soon as recent changes in [jenkins shared library](https://github.com/alexanderbazhenoff/jenkins-shared-library) runs
  ansible playbooks through a shell call by default.

When running scripts ['as part of a pipeline'](#scripts-key), it is also allowed to
[create your own keys](#using-variables-in-scripts-and-playbooks) for the `universalPipelineWrapperBuiltIns` variable.
For example:

```groovy
universalPipelineWrapperBuiltIns.myCustomReport = 'Some text of my custom report'
```

Upon completion of the current script call "as part of a pipeline", these keys will be updated for the entire pipeline.
Built-in pipeline variable keys are not accessible when running scripts ['as part of the pipeline'](#scripts-key), but
they are accessible in environment variables of the same name (see
[Using variables in scripts and playbooks](#using-variables-in-scripts-and-playbooks) and [Example 23](#example-23)):

```groovy
// The value of universalPipelineWrapperBuiltIns.multilineReport can be output as:
println env.multilineReport
```

# Variable substitution

In the configuration file, most string key values can use any pipeline parameter or environment variable (if
substitution is possible, this is indicated in the key description above). It is allowed to use several variables
combined with plain text (see [Example 21](#example-21)). [Built-in pipeline variables](#built-in-pipeline-variables)
substitution is also possible inside the action description (see [Example 22](#example-22)): for example, for variable
substitution of `universalPipelineWrapperBuiltIns.multilineReport` key value, you can just mention the same key name,
like the same way you use environment variable - `$multilineReport` (see [Example 18](#example-18)).

#### Example 21

```yaml
---

# A part of the configuration file with substitution of pipeline parameters
# in the `before_message` and `action` keys.

parameters:
  required:
    - name: FOO
      type: string
    - name: BAR
      type: string
    - name: BAZ
      type: string

stages:
  - name: own stage
    actions:
      - before_message: |
          Starting the action combined from FOO='$FOO', BAR='$BAR' and BAZ='$BAZ' values.
        action: $FOO$BAR$BAZ
```

#### Example 22

```yaml
---

# An example of a configuration file for launching an ansible playbook or pipeline
# (selected by the `ACTION` parameter). The name of the playbook or pipeline is
# specified by the `ACTION_SUBJECT` parameter. The username `USERNAME` is also
# passed to the playbook or pipeline.

parameters:
  required:
    - name: USERNAME
      type: string
      default: 'jenkins'
      description: >-
        Run action under specified username (use in ansible inventory for login
        or pass to downstream pipeline).
    - name: ACTION
      type: choice
      choices:
        - run playbook
        - run pipeline
      description: Choose an action to perform.
    - name: ACTION_SUBJECT
      type: string
      # The default value is set equal to an existing ansible playbook name or a pipeline.
      default: subject_name
      description: Specify an ansible playbook or downstream pipeline name here.

stages:
  # The pipeline `ACTION` parameter will be substituted into the stage name and the first
  # action. The `USERNAME` parameter will also be inserted into the message before the
  # action.
  - name: $ACTION report
    actions:
      - before_message: Ready to $ACTION under $USERNAME
        action: $ACTION
      - action: email report

actions:
  run playbook:
    playbook: $ACTION_SUBJECT
  run pipeline:
    pipeline: $ACTION_SUBJECT
    parameters:
      - name: USERNAME
        type: string
        value: $USERNAME
  email report:
    report: email
    to: '$DEFAULT_REPLYTO'
    subject: Test email report
    # The message will be filled with both environment variables (`JOB_NAME`, `EMAIL`
    # and `BUILD_URL`) and variables built into the pipeline (`currentBuild_result`
    # and `multilineReport`). Note that for built-in variables, you do not need to
    # specify the full name `universalPipelineWrapperBuiltIns` as the value of the
    # `body` key.
    body: |
      Hi,

      I've just run a test for universal jenkins wrapper pipeline for
      '$JOB_NAME' pipeline, finished with '$currentBuild_result' state.
      As you see sending report to $EMAIL done.

      Overall report is:
      $multilineReport

      Check pipeline console for details: $BUILD_URL/console
      This report was generated automatically, please do not reply.

      Sincerely,
      Your CI.
        
playbooks:
  subject_name: |
    - hosts: all
      tasks:
        - name: "Perform ansible ping on the host(s)"
          ansible.builtin.ping:

inventories:
  default: |
    [all]
    192.168.0.200
    192.168.0.201
    [all:vars]
    ansible_connection=ssh
    ansible_become_user=root
    ansible_ssh_common_args='-o StrictHostKeyChecking=no'
    ansible_ssh_user=$USERNAME
    ansible_ssh_pass=my_password
    ansible_become_pass=my_password
```

# Using variables in scripts and playbooks

#### Example 23

#### Example 24

# Usage examples

# URLs