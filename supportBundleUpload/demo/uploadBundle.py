# coding: utf-8

from __future__ import print_function, unicode_literals
import os
from boxsdk import Client
from boxsdk.exception import BoxAPIException
from boxsdk.object.collaboration import CollaborationRole
from auth import authenticate
from boxsdk import JWTAuth
import shelve
import argparse
import sys
import ConfigParser
import datetime
import time
from pprint import pprint

def run_user_example(client):
    # 'me' is a handy value to get info on the current authenticated user.
    me = client.user(user_id='me').get(fields=['login'])
    print('The email of the user is: {0}'.format(me['login']))


def run_folder_examples(client):
    root_folder = client.folder(folder_id='0').get()
    print('The root folder is owned by: {0}'.format(root_folder.owned_by['login']))
    items = root_folder.get_items(limit=100, offset=0)
    print('This is the first 100 items in the root folder:')
    for item in items:
        print("   " + item.name)



def rename_folder(client):
    root_folder = client.folder(folder_id='0')
    foo = root_folder.create_subfolder('foo')
    try:
        print('Folder {0} created'.format(foo.get()['name']))

        bar = foo.rename('bar')
        print('Renamed to {0}'.format(bar.get()['name']))
    finally:
        print('Delete folder bar succeeded: {0}'.format(foo.delete()))


def get_folder_shared_link(client):
    root_folder = client.folder(folder_id='0')
    collab_folder = root_folder.create_subfolder('shared link folder')
    try:
        print('Folder {0} created'.format(collab_folder.get().name))
        shared_link = collab_folder.get_shared_link()
        print('Got shared link:' + shared_link)
    finally:
        print('Delete folder collab folder succeeded: {0}'.format(collab_folder.delete()))


def upload_file(client):
    root_folder = client.folder(folder_id='0')
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'file.txt')
    a_file = root_folder.upload(file_path, file_name='i-am-a-file.txt')
    try:
        print('{0} uploaded: '.format(a_file.get()['name']))
    except BoxAPIException:
        print('{0} upload failed: '.format(a_file.get()['name']))

#     finally:
#         print('Delete i-am-a-file.txt succeeded: {0}'.format(a_file.delete()))

def delete_file(client):
    root_folder = client.folder(folder_id='0')
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'file.txt')
    a_file = root_folder.upload(file_path, file_name='i-am-a-file.txt')
    try:
        print('{0} uploaded: '.format(a_file.get()['name']))
    finally:
        print('Delete i-am-a-file.txt succeeded: {0}'.format(a_file.delete()))

def upload_accelerator(client):
    root_folder = client.folder(folder_id='0')
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'file.txt')
    a_file = root_folder.upload(file_path, file_name='i-am-a-file.txt', upload_using_accelerator=True)
    try:
        print('{0} uploaded via Accelerator: '.format(a_file.get()['name']))
        file_v2_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'file_v2.txt')
        a_file = a_file.update_contents(file_v2_path, upload_using_accelerator=True)
        print('{0} updated via Accelerator: '.format(a_file.get()['name']))
    finally:
        print('Delete i-am-a-file.txt succeeded: {0}'.format(a_file.delete()))


def rename_file(client):
    root_folder = client.folder(folder_id='0')
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'file.txt')
    foo = root_folder.upload(file_path, file_name='foo.txt')
    try:
        print('{0} uploaded '.format(foo.get()['name']))
        bar = foo.rename('bar.txt')
        print('Rename succeeded: {0}'.format(bool(bar)))
    finally:
        foo.delete()


def update_file(client):
    root_folder = client.folder(folder_id='0')
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'file.txt')
    file_v1 = root_folder.upload(file_path, file_name='file_v1.txt')
    try:
        # print 'File content after upload: {}'.format(file_v1.content())
        file_v2_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'file_v2.txt')
        file_v2 = file_v1.update_contents(file_v2_path)
        # print 'File content after update: {}'.format(file_v2.content())
    finally:
        file_v1.delete()


def search_files(client):
    search_results = client.search(
        'i-am-a-file.txt',
        limit=2,
        offset=0,
        ancestor_folders=[client.folder(folder_id='0')],
        file_extensions=['txt'],
    )
    for item in search_results:
        item_with_name = item.get(fields=['name'])
        print('matching item: ' + item_with_name.id)
    else:
        print('no matching items')


def copy_item(client):
    root_folder = client.folder(folder_id='0')
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'file.txt')
    a_file = root_folder.upload(file_path, file_name='a file.txt')
    try:
        subfolder1 = root_folder.create_subfolder('copy_sub')
        try:
            a_file.copy(subfolder1)
            print(subfolder1.get_items(limit=10, offset=0))
            subfolder2 = root_folder.create_subfolder('copy_sub2')
            try:
                subfolder1.copy(subfolder2)
                print(subfolder2.get_items(limit=10, offset=0))
            finally:
                subfolder2.delete()
        finally:
            subfolder1.delete()
    finally:
        a_file.delete()


def move_item(client):
    root_folder = client.folder(folder_id='0')
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'file.txt')
    a_file = root_folder.upload(file_path, file_name='a file.txt')
    try:
        subfolder1 = root_folder.create_subfolder('move_sub')
        try:
            a_file.move(subfolder1)
            print(subfolder1.get_items(limit=10, offset=0))
            subfolder2 = root_folder.create_subfolder('move_sub2')
            try:
                subfolder1.move(subfolder2)
                print(subfolder2.get_items(limit=10, offset=0))
            finally:
                subfolder2.delete()
        finally:
            try:
                subfolder1.delete()
            except BoxAPIException:
                pass
    finally:
        try:
            a_file.delete()
        except BoxAPIException:
            pass


def get_events(client):
    print(client.events().get_events(limit=100, stream_position='now'))


def get_latest_stream_position(client):
    print(client.events().get_latest_stream_position())


def long_poll(client):
    print(client.events().long_poll())


def _delete_leftover_group(existing_groups, group_name):
    """
    delete group if it already exists
    """
    existing_group = next((g for g in existing_groups if g.name == group_name), None)
    if existing_group:
        existing_group.delete()


def run_groups_example(client):
    """
    Shows how to interact with 'Groups' in the Box API. How to:
    - Get info about all the Groups to which the current user belongs
    - Create a Group
    - Rename a Group
    - Add a member to the group
    - Remove a member from a group
    - Delete a Group
    """
    try:
        # First delete group if it already exists
        original_groups = client.groups()
        _delete_leftover_group(original_groups, 'box_sdk_demo_group')
        _delete_leftover_group(original_groups, 'renamed_box_sdk_demo_group')

        new_group = client.create_group('box_sdk_demo_group')
    except BoxAPIException as ex:
        if ex.status != 403:
            raise
        print('The authenticated user does not have permissions to manage groups. Skipping the test of this demo.')
        return

    print('New group:', new_group.name, new_group.id)

    new_group = new_group.update_info({'name': 'renamed_box_sdk_demo_group'})
    print("Group's new name:", new_group.name)

    me_dict = client.user().get(fields=['login'])
    me = client.user(user_id=me_dict['id'])
    group_membership = new_group.add_member(me, 'member')

    members = list(new_group.membership())

    print('The group has a membership of: ', len(members))
    print('The id of that membership: ', group_membership.object_id)

    group_membership.delete()
    print('After deleting that membership, the group has a membership of: ', len(list(new_group.membership())))

    new_group.delete()
    groups_after_deleting_demo = client.groups()
    has_been_deleted = not any(g.name == 'renamed_box_sdk_demo_group' for g in groups_after_deleting_demo)
    print('The new group has been deleted: ', has_been_deleted)


def run_metadata_example(client):
    root_folder = client.folder(folder_id='0')
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'file.txt')
    foo = root_folder.upload(file_path, file_name='foo.txt')
    print('{0} uploaded '.format(foo.get()['name']))
    try:
        metadata = foo.metadata()
        metadata.create({'foo': 'bar'})
        print('Created metadata: {0}'.format(metadata.get()))
        update = metadata.start_update()
        update.update('/foo', 'baz', 'bar')
        print('Updated metadata: {0}'.format(metadata.update(update)))
    finally:
        foo.delete()

def store_tokens_callback_method(access_token, refresh_token):
    # store the tokens at secure storage (e.g. Keychain)
    d =  shelve.open("db.shlv")
    d["access_token"]=access_token
    d["refresh_token"]=refresh_token
    d.close()
    return

def get_auth():
        
    auth = JWTAuth(
        client_id='37vdfnknzax5htrkiler5xkphbxs6f4s',
        client_secret='pMUwYf2g1iAsvFDnCA08ASa1oHwYj3Ut',
        enterprise_id="849101",
        jwt_key_id='h4qpyf9b',
        rsa_private_key_file_sys_path='private_key.pem',
	rsa_private_key_passphrase=b'datos1234',
    )

    access_token = auth.authenticate_instance()
    client = Client(auth)

    print("Upload authenticated successfully")

    return client

def handle_cli():

    parser = argparse.ArgumentParser(description="Document upload to Box through API")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--setup", action="count", help="Setup the Initial Configuration File (One time operation)")
    group.add_argument("-l", "--logs", action="count", help="Upload Support Bundle")
    group.add_argument("-c", "--callhome", action="count", help="Send Call Home Report")
    args = parser.parse_args()    
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    return args

def gen_config_file():

    # Sample config file
    # [General]
    # Customer-Name = "Home Depot"
    # Datos-Cluster-Name = "HD_Staging"
    # Datos-Cluster-Id = 0
    # Box-User-Login = "venkat.reddimanchu@box.com"
    
    # lets create that config file for next time...
    cfgfile = open("box.cfg",'w')
    
    # add the settings to the structure of the file, and lets write it out...
    Config = ConfigParser.RawConfigParser()
    Config.add_section('General')
    Config.set('General', '#Please do not edit the values below.')
    cust_name = raw_input("Please provide customer name:")
    Config.set('General', 'Customer-Name',cust_name)
    datos_name = raw_input("Please provide identifying name for this Datos cluster:")
    Config.set('General', 'Datos-Cluster-Name',datos_name)
    datos_id = raw_input("Please provide identifying id (number) for this Datos cluster (This will be used for further communication w/ Datos):")
    Config.set('General', 'Datos-Cluster-Id',datos_id)
    box_id = raw_input("Please provide login (typically email address) for the user with privileges to the Datos Box folder:")
    Config.set('General', 'Box-User-Login',box_id)
    Config.write(cfgfile)
    cfgfile.close()
    print("Configuration File Generated Successfully")

def get_folder_id(client, folder_name, folder_id=0):
    # get the folder of the folder under folder with id = folder_id
    root_folder = client.folder(folder_id).get()
    try:
        items = root_folder.get_items(limit=100, offset=0)
    except BoxAPIException:
        print('get_items failed')
    for item in items:
#        pprint(vars(item))
#        print('Entry: Name = {0}, ID = {1}, Owned by {2}'.format(item.name, item.id, item.owned_by['login']))
        if (item.name == folder_name):
 #           root_folder = client.folder(item.id)
 #           pprint(vars(root_folder))
 #           print('The root folder {0} is owned by: {1}'.format(root_folder.name, root_folder.owned_by['login']))
            return item.id

def upload_logs(client):

    # Handle case when the folder is empty or the customers folder is not present
    # Handle case with incomplete config file or if config file is not present
    
    config = ConfigParser.RawConfigParser()
    config.read('box.cfg')
    
    datos_customer_name = config.get('General', 'Customer-Name')
    datos_cluster_name = config.get('General', 'Datos-Cluster-Name')
    
    # Create a "SupportBundles_API" folder under root folder
    root_folder_id = 0 #default folder id for root folder
    support_bundle_folder_id = get_folder_id(client, "SupportBundles_API", root_folder_id)
    root_folder = client.folder(support_bundle_folder_id)
    try:
        root_folder.add_collaborator('shalabh.goyal@datos.io', CollaborationRole.EDITOR)
    except:
        pass
    if (support_bundle_folder_id is None):
        root_folder = client.folder(root_folder_id)
        support_bundle_folder = root_folder.create_subfolder("SupportBundles_API")
        support_bundle_folder_id = support_bundle_folder.id

    print ("Support bundle folder id = {0}".format(support_bundle_folder_id))
    # Create a "HomeDepot" folder under "SupportBundles_API" folder
    cust_folder_id = get_folder_id(client, datos_customer_name, support_bundle_folder_id)
    if (cust_folder_id is None):
        root_folder = client.folder(support_bundle_folder_id)
        cust_folder = root_folder.create_subfolder(datos_customer_name)
        cust_folder_id = cust_folder.id

    # Create a "Staging" folder under "HomeDepot" folder
    datos_cluster_folder_id = get_folder_id(client, datos_cluster_name,cust_folder_id)
    if (datos_cluster_folder_id is None):
        root_folder = client.folder(cust_folder_id)
        datos_cluster_folder = root_folder.create_subfolder(datos_cluster_name)
        datos_cluster_folder_id = datos_cluster_folder.id

    # Create a "Timestamp" folder under "Staging" folder
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H') + "_Hrs"
    datos_timestamp_folder_id = get_folder_id(client, timestamp, datos_cluster_folder_id)
    if (datos_timestamp_folder_id is None):
        root_folder = client.folder(datos_cluster_folder_id)
        datos_timestamp_folder = root_folder.create_subfolder(timestamp)
        datos_timestamp_folder_id = datos_timestamp_folder.id

    testVar = raw_input("Please provide name of file to be uploaded:")
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), testVar)
    root_folder = client.folder(datos_timestamp_folder_id)
    a_file = root_folder.upload(file_path, file_name=testVar, upload_using_accelerator=True)
    try:
        print('{0} uploaded: '.format(a_file.get()['name']))
    except BoxAPIException:
        print('{0} upload failed: '.format(a_file.get()['name']))
        print("   " + item.name)
    print('{0} uploaded: '.format(testVar))

def run_collab_examples(client):
    root_folder = client.folder(folder_id='0')
    collab_folder = root_folder.create_subfolder('TestSupportBundle1')
    try:
        print('Folder {0} created'.format(collab_folder.get()['name']))
        collaboration = collab_folder.add_collaborator('shalabh.goyal@datos.io', CollaborationRole.VIEWER)
        print('Created a collaboration')
        try:
            modified_collaboration = collaboration.update_info(role=CollaborationRole.EDITOR)
            print('Modified a collaboration: {0}'.format(modified_collaboration.role))
        finally:
#            collaboration.delete()
            print('Deleted a collaboration')
    finally:
        # Clean up
#        print('Delete folder collab folder succeeded: {0}'.format(collab_folder.delete()))
        print("finally here")


def main():

    args = handle_cli()

    if (args.setup):
        gen_config_file()
    elif (args.logs):
        upload_logs(get_auth())
    elif (args.callhome):
        send_callhome(get_auth())

    os._exit(0)
        
    # run_examples_auth()
    # run_user_example(client)
    # find_folder_examples(client)
    # run_collab_examples(client)
    # # Premium Apps only
    # upload_accelerator(client)



if __name__ == '__main__':
    main()

