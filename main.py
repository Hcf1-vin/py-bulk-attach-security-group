import boto3

client = boto3.client("ec2")

# ID of the security group to be either added or removed
security_group_id = ""

# True = Add security_group_id to instances
# False = Remove security_group_id from instances
append_security_group = True

# Run instance update without actually making any changes
# True = Instance will not be updated
# False = Instance will be updated
dry_run = True


def get_instances():
    # Get a list of all running instances
    paginator = client.get_paginator("describe_instances")
    response_iterator = paginator.paginate(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}],
    )

    # Iterate over the instance list to clean up the output
    instance_list = list()
    for item in response_iterator:

        for reservation in item["Reservations"]:

            for instance in reservation["Instances"]:

                instance_dict = dict()
                instance_dict["InstanceId"] = instance["InstanceId"]
                instance_security_group_list = list()

                for security_group in instance["SecurityGroups"]:
                    instance_security_group_list.append(security_group["GroupId"])

                instance_dict["SecurityGroups"] = instance_security_group_list

                if append_security_group == True and security_group_id not in str(
                    instance_dict["SecurityGroups"]
                ):
                    print(
                        f"Appending {security_group_id} to {instance_dict['SecurityGroups']}"
                    )

                    if len(instance_dict["SecurityGroups"]) < 5:
                        instance_dict["SecurityGroups"].append(security_group_id)
                    else:
                        print(
                            f"Unable to add {security_group_id}. {len(instance_dict['SecurityGroups'])} security groups attached"
                        )
                        continue

                elif append_security_group == False and security_group_id in str(
                    instance_dict["SecurityGroups"]
                ):
                    print(
                        f"Removing {security_group_id} from {instance_dict['SecurityGroups']}"
                    )
                    instance_dict["SecurityGroups"].remove(security_group_id)

                else:
                    # Nothing to do, move to the next item
                    continue

                # Append instance to list of instances to be updated
                instance_list.append(instance_dict)

    if instance_list:
        update_security_groups(instance_list)
    else:
        print("Nothing to update. The instance list is empty")


def update_security_groups(instance_list):

    # iterate over the list of instances to update
    for instance in instance_list:

        print(
            f"Updating InstanceId {instance['InstanceId']} SecurityGroups attribute to {str(instance['SecurityGroups'])}"
        )

        # Update instance security groups
        response = client.modify_instance_attribute(
            InstanceId=instance["InstanceId"],
            Groups=instance["SecurityGroups"],
            DryRun=dry_run,
        )


if __name__ == "__main__":
    get_instances()
