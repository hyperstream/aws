import boto3
import subprocess
import os
import time
import csv

# Initialize a boto3 EC2 resource
ec2 = boto3.resource('ec2')

def get_instances_by_name_tag(name_tag_value):
    """Fetch instances by their 'Name' tag."""
    instances = ec2.instances.filter(
        Filters=[
            {'Name': 'tag:Name', 'Values': [name_tag_value]},
            {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
        ]
    )
    return instances

def start_instance(instance_id):
    """Start an EC2 instance if it is not already running."""
    instance = ec2.Instance(instance_id)
    if instance.state['Name'] != 'running':
        print(f"Starting {instance_id}...")
        instance.start()
        instance.wait_until_running()
        print(f"{instance_id} is now running.")
        return True
    return False

def stop_instance(instance_id):
    """Stop an EC2 instance."""
    print(f"Stopping {instance_id}...")
    instance = ec2.Instance(instance_id)
    instance.stop()
    instance.wait_until_stopped()
    print(f"{instance_id} is now stopped.")

def find_key_for_instance(instance):
    """Find the SSH key for the instance based on its KeyName."""
    key_name = instance.key_name
    keys_directory = os.path.expanduser("~/.ssh")
    for key_file in os.listdir(keys_directory):
        if key_file.startswith(key_name) and key_file.endswith(".pem"):
            return os.path.join(keys_directory, key_file)
    return None

def wait_for_ssh_to_become_available(instance, remote_user, ssh_key_path):
    """Wait until SSH becomes available on the instance."""
    private_ip = instance.private_ip_address
    max_retries = 5
    retry_delay = 20
    ssh_base_cmd = f'ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -i {ssh_key_path} {remote_user}@{private_ip}'

    for attempt in range(max_retries):
        try:
            subprocess.run(f"{ssh_base_cmd} 'echo SSH ready'", shell=True, check=True, stdout=subprocess.PIPE)
            print("SSH is ready.")
            return True
        except subprocess.CalledProcessError:
            print("SSH not yet available, waiting before retrying...")
            time.sleep(retry_delay)
    
    print("SSH did not become available in time.")
    return False

def backup_instance(instance, remote_user):
    """Perform backup operations on the instance."""
    ssh_key_path = find_key_for_instance(instance)
    if not ssh_key_path:
        print(f"No matching SSH key found for instance {instance.id} with KeyName {instance.key_name}")
        return

    private_ip = instance.private_ip_address

    if not wait_for_ssh_to_become_available(instance, remote_user, ssh_key_path):
        print(f"Cannot perform backup as SSH is not available for instance {instance.id}.")
        return

    create_dir_cmd = "sudo mkdir -p /data/backup/ec2-user-home/"
    rsync_cmd = "sudo rsync -av --delete /home/ec2-user/ /data/backup/ec2-user-home/"

    ssh_base_cmd = f'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i {ssh_key_path} {remote_user}@{private_ip}'
    subprocess.run(f"{ssh_base_cmd} '{create_dir_cmd}'", shell=True, check=True)
    subprocess.run(f"{ssh_base_cmd} '{rsync_cmd}'", shell=True, check=True)
    print("Backup completed successfully.")

def read_instance_names_from_csv(file_path='instance_names.csv'):
    """Read instance names from a CSV file."""
    names = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            names.append(row['Name'])
    return names

def main():
    """Main function to process each instance for backup."""
    instance_names = read_instance_names_from_csv()

    for name_tag in instance_names:
        print(f"\nProcessing instances with Name tag: '{name_tag}'")
        instances = get_instances_by_name_tag(name_tag)
        for instance in instances:
            print(f"Found instance: {instance.id}")
            remote_user = "ec2-user"
            was_started = start_instance(instance.id)
            backup_instance(instance, remote_user)
            if was_started:
                stop_instance(instance.id)

if __name__ == "__main__":
    main()
