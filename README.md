ANSIBLE WRAPPER SETTINGS
========================

**WARNING! This repository and ansible wrapper pipelines currently is under development progress. There is no up-to-date
README and properly working code**.

YAML settings for ansible wrapper pipeline(s).

## TLDR

A set of yaml settings for 'universal-ansible-wrapper' pipeline with a format like GitLab CI. The main idea is not to 
write a custom pipelines for every ansible role.

## USAGE

An abstract example of yaml settings for a wrapper looks like:

```yaml
---

parameters:
  required:
    - name: PARAM1
      type: choice
      action: True
      choices:
        - action_name1
        - action_name2
        - action_name3
      description: 'Description of PARAM1'
  optional:
    - name: PARAM2
      type: string
      default: 'default string'
      trim: False
      description: 'Description of PARAM2'
    - name: PARAM3
      type: boolean
      default: False
      description: 'Description of PARAM3'

stages:
  - git_clone_stage
  - ansible_galaxy_install_stage
  - stage_name1
  - stage_name2
  - stage_name3
  - stage_name4

actions:
  git_clone_stage:
    repo_url: ssh://git@gitlab.domain/group/project-name.git
    repo_branch: main
    directory: sub_directory_in_workspace_for_repository 
  ansible_galaxy_install_stage:
    collection: ansible.galaxy.collection_name_to_install
  action_name1:
    playbook: playbook1
    stage: stage_name1
  action_name2:
    playbook: playbook2
    stage: stage_name1
  action_name3:
    stage: stage_name2
    pipeline: name-of-jenkins-pipeline
    parameters:
      - name: DOWNSTREAM_PARAM2
        parameter: PARAM2
      - name: DOWNSTREAM_PARAM3
        parameter: PARAM3
  action_name4:
    stage: stage_name4
    script: script_name1

    
scripts:
  script_name1: |
    // some groovy code here
    println String.format('PARAM2 on value executing %s action is awesome: %s', env.PARAM1, env.PARAM2)


playbooks:
  - name: playbook1
    playbook: |
      - hosts: all
        become: True
        become_method: sudo
        gather_facts: True
      
        tasks:
      
          - name: "Some ansible playbook call on action_name1 choice during stage_name1"
            ansible.builtin.include_role:
              name: some.role.name
            vars:
              role_action: action_name1
              some_role_parameter: $PARAM2
              another_role_parameter: True
  - name: playbook2
    playbook: |
      - hosts: all
        become: True
        become_method: sudo
        gather_facts: True
      
        tasks:
      
          - name: "Some ansible playbook call on action_name2 choice during stage_name1"
            ansible.builtin.include_role:
              name: some.role.name
            vars:
              role_action: action_name2
              some_role_parameter: $PARAM2


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
    ansible_become_pass=$SSH_SUDO_PASSWORD
```
