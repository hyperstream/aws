# EC2 Instance Backup Script

This script is designed to automate the backup process for AWS EC2 instances. It leverages the Boto3 library to interact with AWS services, managing EC2 instances based on their "Name" tag values. The script provides functionality to start, stop, and backup EC2 instances. It also waits for SSH availability to ensure that backup operations can be performed over SSH. Backup operations are carried out using `rsync` to synchronize files from the EC2 instance to a specified backup location.

## Features

- **Instance Management**: Start and stop instances to ensure they are in the correct state for backup.
- **SSH Key Handling**: Automatically finds the SSH key associated with an instance for SSH access.
- **Backup**: Utilizes `rsync` over SSH to backup files from the EC2 instance.
- **Tag Filtering**: Filter instances based on the "Name" tag to selectively backup certain instances.
- **CSV Support**: Read instance names from a CSV file to manage backups for multiple instances.

## Prerequisites

- AWS account with access to EC2 instances.
- Python 3.x installed.
- Boto3 library installed (`pip install boto3`).
- Proper AWS credentials configured (via AWS CLI or Boto3 configuration).
- SSH keys for instances stored in `~/.ssh` directory.
- Instances must be tagged with a "Name" tag for identification.

## Setup

1. **AWS Credentials**: Ensure your AWS credentials are set up in `~/.aws/credentials` or configured through environment variables.
2. **SSH Key Access**: Make sure the SSH private keys for your instances are stored in `~/.ssh` and are named according to the instance's `KeyName` attribute.

## Usage

1. **Prepare the CSV File**: Create a CSV file named `instance_names.csv` with a column `Name` listing the "Name" tags of instances you want to backup.

Example CSV content:
```
Name
MyInstance1
MyInstance2
```

2. **Run the Script**: Execute the script with Python.

```bash
python ec2_backup.py
```

The script will process each instance listed in the CSV file, starting them if necessary, performing the backup, and stopping them if they were started by the script.

## Functions Overview

- `get_instances_by_name_tag(name_tag_value)`: Fetch instances by their "Name" tag.
- `start_instance(instance_id)`: Start an EC2 instance if it's not already running.
- `stop_instance(instance_id)`: Stop an EC2 instance.
- `find_key_for_instance(instance)`: Find the SSH key for the instance.
- `wait_for_ssh_to_become_available(instance, remote_user, ssh_key_path)`: Wait for SSH to become available on the instance.
- `backup_instance(instance, remote_user)`: Perform backup operations on the instance.
- `read_instance_names_from_csv(file_path='instance_names.csv')`: Read instance names from a CSV file.
- `main()`: Main function to orchestrate the backup process.

## Customization

- Modify `read_instance_names_from_csv` to change the CSV file path or structure.
- Adjust `backup_instance` to customize backup operations, such as changing the backup directory or using a different synchronization tool.

## Notes

- Ensure that your AWS IAM user has the necessary permissions to manage EC2 instances and access related resources.
- Verify that the SSH service is running on the instances and accessible from your network.
- This script assumes the default user for Amazon Linux instances (`ec2-user`), adjust accordingly for instances with different operating systems.

For detailed documentation on Boto3 and its EC2 service, refer to the [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html).
